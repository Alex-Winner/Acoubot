import socket
import pickle
from scipy.io import wavfile
import scipy.signal
import simpleaudio as sa
import wavio
import acoustics
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import csv
import os
import solution_algo
import AudioAnalyzer
import mapping




def multifilesend(port,sock,room_name,benchmark_num):
    try:
        ## Create a TCP/IP socket
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ## Connect the socket to the port where the server is listening
        #server_address = ('192.168.1.201', port)
        #print('connecting to %s port %s' % server_address)
        #sock.connect(server_address)

        for point_num in range(5):
            print(point_num+1)
            #path='./multitest/test'+str(x+1)+'.wav'
            record_path = ('./Room/'+room_name+'/'+benchmark_num
                                    +'/'+str(point_num+1)+'/Records/measurepoint '
                                                +str(point_num+1)+'.wav')
            
            
            
            with open(record_path, 'wb') as measure_point_wav:
                while True:
                    wav_file = sock.recv(1024)
                    if not wav_file:
                        break
                    measure_point_wav.write(wav_file)
            print('end')

            ###after reciving file use this lines of code###
            ###to close and open socket again to 
            sock.close
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('192.168.1.200', port)
            sock.connect(server_address)
            #### end of lines of reciving####



    except Exception as e:
        print(e)
        print('MU not found')

def existing_bench(selected_room):
    list_of_bench=os.listdir('./Room/'+selected_room+'/')
    return list_of_bench

def existing_directory():
    list_of_rooms=os.listdir('./Room/')
    return list_of_rooms

# define the name of the directory to be created

def create_directory(room_name):
    benchmark_num = datetime.now().strftime("%d_%m_%y_%H%M%S")
    if os.path.isdir('./Room/'+room_name) == False:
        room_path='./Room/'+room_name
        try:
            os.mkdir(room_path)
        except OSError:
            print ("Creation of the directory %s failed" % room_path)
    
    bench_path='./Room/'+room_name+'/'+benchmark_num
    try:
        os.mkdir(bench_path)
    except OSError:
        print ("Creation of the directory %s failed" % bench_path)
    
    for point_num in range(5):
        point_path='./Room/'+room_name+'/'+benchmark_num+'/'+str(point_num+1)
        try:
            os.mkdir(point_path)
        except OSError:
            print ("Creation of the directory %s failed" % point_path)
    
    for point_num in range(5):
        map_path = './Room/'+room_name+'/'+benchmark_num+'/'+str(point_num+1)+'/Maps'
        record_path = './Room/'+room_name+'/'+benchmark_num+'/'+str(point_num+1)+'/Records'
        plot_path = './Room/'+room_name+'/'+benchmark_num+'/'+str(point_num+1)+'/Plots'

        try:
            os.mkdir(record_path)
        except OSError:
            print ("Creation of the directory %s failed" % record_path)
        try:
            os.mkdir(map_path)
        except OSError:
            print ("Creation of the directory %s failed" % map_path)
        try:
            os.mkdir(plot_path)
        except OSError:
            print ("Creation of the directory %s failed" % plot_path)
    return  benchmark_num

def height_command(height_msg,sock):
    try:
        message = pickle.dumps(height_msg)  # 1 = Record, 2 =
        print('sending measure height massage')
        sock.sendall(message)

        # Look for the response
        height_of_the_room = sock.recv(1024)
        height_of_the_room = pickle.loads(height_of_the_room)
        print('Height = ' + str(height_of_the_room))

    finally:
        print('closing socket')
        sock.close()

    return height_of_the_room

def measure_command(record_msg,sock,sine_sweep_name,record_path):
    try:
        # Send data
        message = pickle.dumps(record_msg)  # 1 = Record, 2 =
        print('sending record command')
        sock.sendall(message)

        #time.sleep(2)
        # Look for the response
        print('reciving begin recording message')
        data = sock.recv(1024)
        print(data.decode('UTF-8'))

        #print('SU - sleep')
        time.sleep(5)
        #print('SU - play')
        wave_obj = sa.WaveObject.from_wave_file(sine_sweep_name)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing

        print('reciving recording done message')
        data = sock.recv(1024)
        print(data.decode('UTF-8'))

        #time.sleep(1)
        #print('reciving recording file')
        #with open(record_path, 'wb') as measure_point_wav:
        #    while True:
        #        wav_file = sock.recv(1024)
        #        if not wav_file:
        #            break
        #        measure_point_wav.write(wav_file)
        #print('finish reciving file')
        #print(measure_point_wav)

    # except:
    #    print('massage not sent')

    finally:
        print('recording finished')
        #sock.close()
        time.sleep(3)
        #sock=connection()
        
def mapping_command(mapping_msg,sock):
    try:
        # Send data
        message = pickle.dumps(mapping_msg)  # 3 = mapping
        print('sending mapping massage')
        sock.sendall(message)

        # Looking for the response
        data = sock.recv(1024)
        print(data.decode('UTF-8')) #expect to recieve "scanning room"

        time.sleep(1)
        data_stat = 0
        while data_stat != '1' and data_stat != '2':
            data = sock.recv(1024)
            data_stat = data.decode('UTF-8')
            if data_stat == '2':
                break
            if data_stat == '1':
                break
            print(data_stat)
        
        time.sleep(1)
        if data == 'Scan Failed':
            return
        else:
            
            # Receiving map data
            with open(map_path, 'wb') as room_map:
                while True:
                    map_file = sock.recv(1024)
                    if not map_file:
                        break
                    room_map.write(map_file)
            time.sleep(3)
            
            # Receiving basic values data
            #bv_file=sock.recv(1024)
            #with open(bv_path, 'wb') as basic_values:
            #    while True:
            #        bv_file = sock.recv(1024)
            #        if not bv_file:
            #            break
            #        basic_values.write(bv_file)
            #basic_values=pickle.loads(bv_file)

    # except:
    #    print('massage not sent')

    finally:
        print('closing socket')
        sock.close()
        #print(basic_values)

def closeconnection_command(sock):
    try:
        closeconnection_cmd=5
        closeconnection_message=(closeconnection_cmd,'close connection')
        message = pickle.dumps(closeconnection_message)  # 1 = Record, 2 =
        sock.sendall(message)

    finally:
        print('closing socket')
        sock.close()
    
def plot_rect(point_num,room_name,benchmark_num,bands, data, data_label, xx_label, yy_label, rect_title, colour='g' ):
    x = np.arange(len(bands))
    width = 0.35

    fig = plt.figure(figsize=(13, 8))
    plt.ioff()
    ax = fig.add_subplot(111)
    ax.bar(x, data, width, label=data_label, color=colour)
    ax.set_xlabel(xx_label)
    ax.set_ylabel(yy_label)
    ax.set_title(rect_title)
    ax.set_xticks(x)
    ax.set_xticklabels(bands)
    ax.legend()
    plt.savefig('./Room/'+room_name+'/'+benchmark_num+'/'+str(point_num)+'/Plots/' + rect_title + '.png', dpi=300, facecolor='#FCFCFC')

    return None

def plot_2rect(point_num,room_name,benchmark_num,bands, data_1, data_label_1, data_2, data_label_2, xx_label,
               yy_label, rect_title, colour1='m', colour2='g'):
    x = np.arange(len(bands))
    width = 0.35

    fig = plt.figure(figsize=(13, 8))
    plt.ioff()

    ax = fig.add_subplot(111)
    ax.bar(x + width / 2, data_1, width, label=data_label_1, color=colour1)
    ax.bar(x - width / 2, data_2, width, label=data_label_2, color=colour2)
    ax.set_xlabel(xx_label)
    ax.set_ylabel(yy_label)
    ax.set_title(rect_title)
    ax.set_xticks(x)
    ax.set_xticklabels(bands)
    ax.legend()
    plt.savefig('./Room/'+room_name+'/'+benchmark_num+'/'+str(point_num)+'/Plots/' + rect_title + '_2.png',
                dpi=100, facecolor='#FCFCFC')

    return None

def plot_4rect(point_num,room_name,benchmark_num,bands, data_1, data_label_1, data_2, data_label_2,data_3,data_label_3,data_4,data_label_4, xx_label,
               yy_label, rect_title, colour1='m', colour2='g'):
    x = np.arange(len(bands))
    width = 0.1

    fig = plt.figure(figsize=(13, 8))
    plt.ioff()

    ax = fig.add_subplot(111)
    ax.bar(x - width - width / 2 , data_1, width, label=data_label_1, color=colour1)
    ax.bar(x - width + width / 2 , data_2, width, label=data_label_2, color=colour2)
    ax.bar(x + width - width / 2 , data_3, width, label=data_label_3, color='r')
    ax.bar(x + width + width / 2 , data_4, width, label=data_label_4, color='c')
    ax.set_xlabel(xx_label)
    ax.set_ylabel(yy_label)
    ax.set_title(rect_title)
    ax.set_xticks(x)
    ax.set_xticklabels(bands)
    ax.legend()
    plt.savefig('./Room/'+room_name+'/'+benchmark_num+'/'+str(point_num)+'/Plots/' + rect_title + '_2.png',
                dpi=100, facecolor='#FCFCFC')

    return None

def connection(port):
    # -----------------------------------
    # --------WIFI CONNECTION------------
    # -----------------------------------

    try:
       # Create a TCP/IP socket
       sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       # Connect the socket to the port where the server is listening
       server_address = ('192.168.1.200', port)
       print('connecting to %s port %s' % server_address)
       sock.connect(server_address)
       return sock
    except:
        print('MU not found')
        return sock

def benchmark(port,room_name,benchmark_num,sock):
    # ---------------------------------
    # --------Signal creator-----------
    # ---------------------------------
    #benchmark_num=str(benchmark_num)
    # Sweep Parameters
    start_frequency = 1        # Hz
    stop_frequency = 20000      # Hz
    sweep_duration = 5          # Sec
    time_start = 0
    sample_rate = 48000
    amplitude_dbfs = -5        # dB


    sine_sweep, inv_sine_sweep, time_vector, t_impulse = AudioAnalyzer.create_sweep(start_frequency, stop_frequency,
                                                                                    sweep_duration, time_start,
                                                                                    sample_rate, amplitude_dbfs)

    sine_sweep_name = "./Signal/sine_sweep.wav"
    wavio.write(sine_sweep_name, sine_sweep, sample_rate, sampwidth=3)
    
    
    try:
        Go_to_point_cmd = 2
        gotopoint_message=(Go_to_point_cmd,'Go to Point')
        message = pickle.dumps(gotopoint_message)  # 1 = Record, 2 =
        sock.sendall(message)
        print('recieving confiramtion go to point from MU')
        data = sock.recv(1024)
        
        time.sleep(1)
        for point_num in range(5):
            print('recieving ready message from MU')
            data = sock.recv(1024)
            MU_status=data.decode('UTF-8')
            print(MU_status)
            if MU_status=='MU is Ready':
                Record_cmd = 1
                Record_time = 12
                Record_name = 'Measure_point'
                Record_msg = (Record_cmd, Record_time, Record_name)
                record_path = ('./Room/'+room_name+'/'+benchmark_num
                                    +'/'+str(point_num+1)+'/Records/measurepoint '
                                                +str(point_num+1)+'.wav')
                measure_command(Record_msg,sock,sine_sweep_name,record_path)
        multifilesend(port,sock,room_name,benchmark_num)
        
            
        
        for point_num in range(5):
            try:
                record_path = ('./Room/'+room_name+'/'+benchmark_num
                        +'/'+str(point_num+1)+'/Records/measurepoint '
                        +str(point_num+1)+'.wav')
                analyze_and_solve(point_num+1,record_path,inv_sine_sweep,
                  sample_rate,sine_sweep,room_name,
                  benchmark_num,time_vector,
                  start_frequency, stop_frequency,t_impulse)
                
                
            except Exception as e:
                print(e)
                print('analyze and solve failed')

    except Exception as ee:
        print(ee)
        print('fail')
    
    
    
    '''''
    # -----------------------------------
    # --------COMMANDS and messages------
    # -----------------------------------
    #directories
    #record_path = './Room/'+room_name+'/'+benchmark_num+'/Records/mp1.wav'
    #map_path = './Room/'+room_name+'/'+benchmark_num+'/Maps/mapbytes.p'
    #bv_path = './Room/'+room_name+'/'+benchmark_num+'/Maps/basicvalues.p'
    
    
    # Commands
    #Record_cmd = 1
    #Go_to_point_cmd = 2
    #Mapping_cmd = 3
    #Height_cmd = 4
    

    # messages
    #Record_time = 12
    #Record_name = 'Measure_point'
    #Record_msg = (Record_cmd, Record_time, Record_name)
    #
    #mapping_room_name = 'test'
    #
    #mapping_msg = (Mapping_cmd, mapping_room_name, benchmark_num)
    #
    #height_msg = (Height_cmd, 'Height_cmd')
    #
    #mapping_command(mapping_msg,sock)
    #measure_command(Record_msg,sock,sine_sweep_name,record_path)
    #height_command(height_msg,sock)
    
    # ---------------------------------
    # ----------Go to Point------------
    # ---------------------------------
    '''''


    
   
    ##prepare for function:record_path,inv_sine_sweep,sample_rate,sine_sweep,room_name,benchmark_num

def analyze_and_solve(point_num,record_path,inv_sine_sweep,
                      sample_rate,sine_sweep,room_name,
                      benchmark_num,time_vector,
                      start_frequency, stop_frequency,t_impulse):

    # ---------------------------------
    # --------Map Creator---------
    # ---------------------------------

    #map_data = mapping.map_creator(map_path)
    #Alex's Room
    #        Ceiling,   floor,      window, computer,   3d printer, bookshelf,  restroom,   bed
    #S = np.sum([12.8726,   12.8726,    8.4836,      8.4836,
    #           3.35282,    2.159,      5.1308,      10.6426])
    #V = 32.969404
    #
    ## window(without the window itself),
    #S_tunable_wall = np.sum([5,      3.35282,    2.159,      5.1308,     10.6426])

    #Guy's Room
    #small=0.55*(1.95-1.2)
    #medium=1.745*1.8
    #big=(3.26-0.55)*1.95
    #fl_and_ceil=big+medium+small
    #
    #V=round(2.66*(fl_and_ceil),2)
    #
    #wall_sum=np.sum([1.8,1.745,3.26,1.95,3.26,0.15,1.745])
    #height=2.66
    #S=(wall_sum*height)+(2*fl_and_ceil)
    #S_tunable_wall=np.sum([2.71+0.75+1.745,1.4])

    #shenkar classroom 204
    floor=4.3*9.3
    V=round(2.66*(floor),2)
    wall_sum=np.sum([9.3,4.3,9.3,4,3])
    height=2.7
    S=(wall_sum*height)+(2*floor)
    S_tunable_wall=round(np.sum([(5.5*2.4),(4.3*2.7),(9.3*1.5)]))

    # ---------------------------------
    # --------Signal analyze-----------
    # ---------------------------------
    

    ir_path = "./Analyzer/impulse_response.wav"
    figure_save_directory = 'Room/'+room_name+'/'+benchmark_num+'/'+str(point_num)+'/Plots'

    #RT_60, ir, spl_bands, spl_bands_a, spl_noise, db_a, bands_noise, bands_reverb = AudioAnalyzer.record_analyzer(inv_sine_sweep,
    #                                                                                                   record_path,
    #                                                                                                   ir_path,
    #                                                                                                   figure_save_directory,
    #                                                                                                   sample_rate
    #                                                                                                   )
    #print('Mean RT_60 recorded = ' + str("{:.2f}".format(np.mean(RT_60))))
    RT_60_third,RT_60, ir, spl_bands, spl_bands_a,spl_noise, db_a, bands_noise, bands_reverb = AudioAnalyzer.record_analyzer(inv_sine_sweep,
                                                                                                       record_path,
                                                                                                       ir_path,
                                                                                                       figure_save_directory,
                                                                                                       sample_rate
                                                                                                       )
    print('Mean RT_60 recorded = ' + str("{:.2f}".format(np.mean(RT_60))))


    #wavio.write(ir_path, ir, sample_rate, sampwidth=3)

    freq_signal, Xdb = AudioAnalyzer.db_fft(sine_sweep, sample_rate)
    freq_record, Fdb = AudioAnalyzer.db_fft(inv_sine_sweep, sample_rate)
    freq, IRdb = AudioAnalyzer.db_fft(ir, sample_rate)


    # ---------------------------------
    # --------Solution Creator---------
    # ---------------------------------

    #high RT60 simulation data

    #match_noise_name, match_noise_spect, dba_state, 
    #db_a=db_a+80
    match_noise_name, match_noise_spect, dba_state = solution_algo.problem2solution_noise(db_a, spl_bands)


    #when mode is 1 the the system checks RT60 
    #not every measuring point needs to be checked
    #for RT60

    mode=1

    if mode==1:
        RT_60 = np.array(RT_60) #+ 0.4 
        SAC, RT60_TOP3 = solution_algo.problem2solution_rt60( RT_60, V, S, S_tunable_wall)


    # --------------------------------------
    # ---------------PLOT-------------------
    # --------------------------------------
    plot_rect(point_num,room_name,benchmark_num,bands_reverb, RT_60, 'RT_60',
              '1/3 octave bands [Hz]', 'Time[sec]', 'RT60 value', 'c')

    #data1 = SAC
    #data_label1 = 'Measured alpha coef Bands'
    #data2 = match_RT60_spect
    #data_label2 = match_RT60_name
    #x_label = 'octave bands [Hz]'
    #y_label = 'Sound absorption coefficient'
    #title = 'Sound absorption coefficients'
    #
    #plot_2rect(bands_reverb, data1, data_label1, data2,
    #           data_label2, x_label, y_label, title, 'y', 'b')


    data1 = RT_60
    data_label1 = 'Measured RT60 Bands'
    data2 = RT60_TOP3[1, 1]
    data_label2 = RT60_TOP3[1, ::2]
    data3 = RT60_TOP3[2, 1]
    data_label3 = RT60_TOP3[2, ::2]
    data4 = RT60_TOP3[3, 1]
    data_label4 = RT60_TOP3[3, ::2]
    x_label = 'octave bands [Hz]'
    y_label = 'Time[sec]'
    title = 'RT60 after test'

    plot_4rect(point_num,room_name,benchmark_num,bands_reverb, data1, data_label1, data2,
               data_label2, data3, data_label3, data4,
               data_label4, x_label, y_label, title, 'y', 'b')

    data1 = spl_bands
    data_label1 = 'Measured SPL Bands'
    data2 = match_noise_spect
    data_label2 = match_noise_name
    x_label = 'octave bands [Hz]'
    y_label = 'dB SPL'
    title = 'Noise match Octave Bands'

    plot_2rect(point_num,room_name,benchmark_num,bands_noise, data1, data_label1, data2,
               data_label2, x_label, y_label, title, 'y', 'b')

    height_space_plot = 0.3

    figure_log_sweep = plt.figure(figsize=(13, 8))
    plt.style.use('ggplot')
    plt.rcParams['font.size'] = 10
    plt.subplots_adjust(hspace=height_space_plot)
    time_log_sweep_plot = figure_log_sweep.add_subplot(211)
    plt.plot(time_vector, sine_sweep)
    plt.xlabel('Time [Sec]')
    plt.ylabel('Amplitude')
    time_log_sweep_plot.set_title('Logarithmic sine sweep in time')
    frequency_log_sweep_plot = figure_log_sweep.add_subplot(212)
    plt.plot(freq_signal, Xdb)
    frequency_log_sweep_plot.set_xscale('log')
    plt.xlabel('Frequency Log scale [Hz]')
    plt.ylabel('Magnitude [dBFS]')
    frequency_log_sweep_plot.set_title('Logarithmic sine sweep spectrum')
    plt.xticks(AudioAnalyzer.ticks, AudioAnalyzer.labels)
    frequency_log_sweep_plot.set(
        xlim=(start_frequency, stop_frequency), ylim=(-40, 10))
    frequency_log_sweep_plot.set_xlim(10, 30e3)
    plt.savefig('./' + figure_save_directory +
                '/Test_signal.png', dpi=100, facecolor='#FCFCFC')

    figure_inverse_log_sweep = plt.figure(figsize=(13, 8))
    plt.subplots_adjust(hspace=height_space_plot)
    time_inverse_log_sweep_plot = figure_inverse_log_sweep.add_subplot(211)
    plt.plot(time_vector, inv_sine_sweep)
    plt.xlabel('Time [Sec]')
    plt.ylabel('Amplitude')
    time_inverse_log_sweep_plot.set_title(
        'Inverse filter - Logarithmic Sine sweep')
    freq_inv_log_sweep_plot = figure_inverse_log_sweep.add_subplot(212)
    plt.plot(freq_record, Fdb)
    freq_inv_log_sweep_plot.set_xscale('log')
    plt.xlabel('Frequency Log scale [Hz]')
    plt.ylabel('Magnitude [dBSF]')
    freq_inv_log_sweep_plot.set_title('Inverse filter - spectrum')
    plt.xticks(AudioAnalyzer.ticks, AudioAnalyzer.labels)
    freq_inv_log_sweep_plot.set(
        xlim=(start_frequency, stop_frequency), ylim=(-40, 10))
    freq_inv_log_sweep_plot.set_xlim(10, 30e3)
    plt.savefig('./' + figure_save_directory +
                '/Inverse_filter.png', dpi=100, facecolor='#FCFCFC')

    freq_response = plt.figure(figsize=(13, 8))
    plt.subplots_adjust(hspace=height_space_plot)
    IRF = freq_response.add_subplot(211)
    plt.plot(t_impulse, ir)
    plt.xlabel('Time [Sec]')
    plt.ylabel('Amplitude')
    IRF.set_title('Impulse response')
    TF = freq_response.add_subplot(212)
    plt.plot(freq, IRdb)
    TF.set_xscale('log')
    TF.set(xlim=(start_frequency, stop_frequency), ylim=(-80, 10))
    plt.xlabel('Frequency Log scale [Hz]')
    plt.ylabel('Magnitude [dBFS]')
    TF.set_title('Transmit Function')
    plt.xticks(AudioAnalyzer.ticks, AudioAnalyzer.labels)
    TF.set_xlim(10, 30e3)
    plt.savefig('./' + figure_save_directory +
                    '/Impulse_response.png', dpi=100, facecolor='#FCFCFC')
    plt.close('all')


####tests#######

#room_name='test17'
#benchmark_num=create_directory(room_name)
#sock=connection()
#port=10001
##sock=1
#
##benchmark_num='26_06_21_114926'
#benchmark(port,room_name,benchmark_num,sock)