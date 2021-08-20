import numpy as np
import scipy.signal as signal
import acoustics
from scipy.io import wavfile
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.io import wavfile
import wavio
import simpleaudio as sa


labels = ['10', '20', '30', '', '50', '', '', '', '',
          '100', '200', '300', '', '500', '', '', '', '',
          '1K', '2k', '3k', '', '5K', '', '', '', '',
          '10K', '20K']
ticks = [10, 20, 30, 40, 50, 60, 70, 80, 90,
         100, 200, 300, 400, 500, 600, 700, 800, 900,
         1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
         10000, 20000]
height_space_plot = 0.3
db_ref = 0.00002        # 2pP


def dbfs_to_amp(dBfs):
    """
    Args:
        dBfs: dBfs value

    Returns: Amplitude of a signal
    """
    return 10 ** (dBfs/20)


def amp_to_dbfs(amp):
    """
    Only for 24 bit signal
    Args:
        amp: Amplitude of a signal

    Returns: dBfs value
    """
    return 20 * np.log10(np.abs(amp)/(2**23-1))


def db_fft(signal, fs, win=None):
    N = len(signal)  # Length of input sequence

    if win is None:
        win = np.ones(signal.shape)
    if len(signal) != len(win):
        raise ValueError('Signal and window must be of the same length')
    signal = signal * win

    # Calculate real FFT and frequency vector
    sp = np.fft.rfft(signal)
    freq_vector = np.arange((N / 2) + 1) / (float(N) / fs)

    # Scale the magnitude of FFT by window and factor of 2,
    # because we are using half of FFT spectrum.
    s_mag = np.abs(sp) * 2 / np.sum(win)

    # Convert to dBFS
    ref = s_mag.max()
    s_dbfs = 20 * np.log10(s_mag / ref)
    return freq_vector, s_dbfs


def create_sweep(start_frequency,
                 stop_frequency,
                 duration,
                 time_start,
                 sample_rate,
                 amplitude_dbfs):
    """

    Args:
        start_frequency:
        stop_frequency:
        duration:
        time_start:
        sample_rate:
        amplitude_dbfs:

    Returns:

    """
    time_vector = np.arange(time_start, duration * sample_rate) / sample_rate
    t_impulse = np.arange(-sample_rate / 2, sample_rate / 2) / sample_rate
    R = np.log(stop_frequency / start_frequency)
    amplitude = dbfs_to_amp(amplitude_dbfs)

    # ESS generation
    sine_sweep = amplitude * np.sin((2 * np.pi * start_frequency * duration / R) * (np.exp(time_vector * R / duration) - 1))
    # Inverse filter
    k = np.exp(time_vector * R / duration)
    inverse_sine_sweep = sine_sweep[::-1] / k

    return sine_sweep, inverse_sine_sweep, time_vector, t_impulse

def cross_cor(recorded):
    sine_sweep_name = "./Signal/sine_sweep.wav"
    fs,sweep = wavfile.read(sine_sweep_name)
    corr = signal.correlate(sweep, recorded)
    return

def record_analyzer(inv_sine_sweep, record_path, ir_path, figure_save_directory,sample_rate):

    first_noise = 63
    last_noise = 10000
    first_reverb = 125
    last_reverb = 4000
    bands_noise_third = acoustics.bands.third(first_noise, last_noise)
    bands_noise_octave = acoustics.bands.octave(first_noise, last_noise)
    bands_reverb = acoustics.bands.octave(first_reverb, last_reverb)

    fs, m_point_sample = wavfile.read(record_path)
    
    #original
    #background_noise_sample = m_point_sample[:5*fs]
    #sine_sweep_sample = m_point_sample[5*fs:]
    #temp
    background_noise_sample = m_point_sample[:4*fs]
    sine_sweep_sample = m_point_sample[4*fs:]
    #cross_cor(sine_sweep_sample)

    time_background_noise = np.arange(0, background_noise_sample.shape[0])/fs
    time_sine_sweep = np.arange(0, sine_sweep_sample.shape[0])/fs

    # mic sensitivity correction and bit conversion
    # "Sens Factor = 3.2378dB, AGain = 18dB, SERIAL NO: 7071178"
    mic_sens_dBV = -3.2378  # mic sensitivity in dBV + any gain
    AGain = -18      # dB
    USB_Voltage = 5.00
    chunk = 48000   # 8192
    #original
    #mic_sens_corr = np.power(10.0, (mic_sens_dBV + AGain) / 20.0)  # calculate mic sensitivity conversion factor

    mic_sens_corr = np.power(10.0, (-43.3) / 20.0)  # calculate mic sensitivity conversion factor
    
    # (USB=5V, so 23 bits are used (the 24th for negatives)) and the manufacturer microphone sensitivity corrections
    noise_pressure_pascal = mic_sens_corr * ((background_noise_sample / np.power(2.0, 23)) * USB_Voltage)
    sine_pressure_pascal = mic_sens_corr * ((sine_sweep_sample / np.power(2.0, 23)) * USB_Voltage)

    # compute FFT parameters

    f_vec = fs * np.arange(chunk / 2) / chunk  # frequency vector based on window size and sample rate
    mic_low_freq = 20  # low frequency response of the mic
    low_freq_loc = np.argmin(np.abs(f_vec - mic_low_freq))
    fft_data = (np.abs(np.fft.fft(noise_pressure_pascal))[0:int(np.floor(chunk / 2))]) / chunk
    fft_data[1:] = 2 * fft_data[1:]

    calibration_file = np.genfromtxt('7071178.csv', dtype='float', delimiter=',')
    freq_calibration = calibration_file[:, 0]
    dB_calibration = calibration_file[:, 1]
    dB_calibration_int = interpolate.interp1d(freq_calibration, dB_calibration, kind='cubic', fill_value="extrapolate")

    Noise_freq, Noise_dB = db_fft(noise_pressure_pascal, 48000)
    dB_calibration_int = dB_calibration_int(Noise_freq)
    #original
    #noise_calibrated_dB = Noise_dB + dB_calibration_int
    noise_calibrated_dB = Noise_dB 
    noise_pressure_pascal_calibrated = np.fft.irfft(noise_calibrated_dB, n=None, axis=-1, norm=None)
    spl_bands_third = acoustics.signal.third_octaves(noise_pressure_pascal, fs, density=False,
                                                     frequencies=bands_noise_third, ref=2e-05)

    spl_bands_octave = acoustics.signal.third_octaves(noise_pressure_pascal, fs, density=False,
                                                      frequencies=bands_noise_octave, ref=2e-05)
    #Test calibration
    noise_cal_test=[0.85047785,0.842108119,0.84067022,0.864368019,0.843995471,0.939400485,0.883493493,0.88811988,0.883617633,0.877940678,0.900861004,0.894754341,0.91179263,0.936354099,0.9951282,1.044870647,1.078167793,1.130624871,1.153016061,1.186072926,1.206430308
                    ]
      
    spl_noise = spl_bands_third[1]#*noise_cal_test

    # A-weighting
    spl_bands_a = acoustics.weighting.a_weighting(bands_noise_third[0], bands_noise_third[-1])
    
    spl_bands_a_weighted = spl_noise + spl_bands_a
    db_a =0.8+ (10 * np.log10(np.sum(np.power(10, spl_bands_a_weighted / 10))))
    print('dB(a) = ' + str("{:.2f}".format(db_a)))

    # Impulse response
    ir = signal.fftconvolve(inv_sine_sweep, sine_sweep_sample, mode='same')
    max_ir = np.where(ir == np.max(ir))
    max_ir = max_ir[0]
    time_start = int(max_ir - 0.5 * fs)
    time_stop = int(max_ir + 0.5 * fs)
    ir = ir[time_start:time_stop]
    wavio.write(ir_path, ir, sample_rate, sampwidth=3)
    # Get spectra of noise
    BGN_freq, BGN_dB = db_fft(background_noise_sample, 48000)

    # Get RT_60 time
    RT_60 = acoustics.room.t60_impulse(ir_path, bands_reverb, rt='t20')
    
    # Plots
    plt.ioff()
    mp = plt.figure(figsize=(13, 8))
    plt.style.use('ggplot')
    plt.rcParams['font.size'] = 10
    plt.subplots_adjust(hspace=height_space_plot)

    mp_time = mp.add_subplot(211)
    plt.plot(time_background_noise, noise_pressure_pascal)
    plt.xlabel('Time [Sec]')
    plt.ylabel('Amplitude [Pa]')
    mp_time.set_title('background noise sample')

    mp_time = mp.add_subplot(212)
    plt.plot(time_sine_sweep, sine_pressure_pascal)
    plt.xlabel('Time [Sec]')
    plt.ylabel('Amplitude [Pa]')
    mp_time.set_title('Sine sweep sample')

    plt.savefig('./' + figure_save_directory + '/Sample.png', dpi=100, facecolor='#FCFCFC')
    
    
    #debugging
    #print(RT_60_third)
    #print(spl_noise)
    RT_60_third = acoustics.room.t60_impulse(ir_path,  bands_noise_third, rt='t20')
    #a = np.asarray([RT_60_third])
    #np.savetxt('./' + figure_save_directory +'RT60.csv', a, delimiter=",")
    
    #original
    #return RT_60, ir, spl_bands_octave[1], spl_bands_a_weighted,spl_noise, db_a, bands_noise_octave, bands_reverb
    #experiment
    return RT_60_third, RT_60, ir, spl_bands_octave[1], spl_bands_a_weighted, spl_noise, db_a, bands_noise_octave, bands_reverb
