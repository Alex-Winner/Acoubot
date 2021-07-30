import pyaudio
import wave


form_1 = pyaudio.paInt24   # 24-bit resolution
chans = 1                  # 1 channel
samp_rate = 48000          # 48kHz sampling rate
chunk = 8192 # 2^13 samples for buffer
record_secs = 5 # seconds to record
dev_index = 1 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'CONNECT.wav' # name of .wav file

def measure(rec_time=12, wav_name='deafult.wav'):
    p = pyaudio.PyAudio()
    for ii in range(p.get_device_count()):
        print(p.get_device_info_by_index(ii).get('name'))

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*rec_time)):
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    path = './recording/'+wav_name 
    wavefile = wave.open(path,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()

    