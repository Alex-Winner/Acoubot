import socket
import sys
import Recording
import pickle
#import Test_Motor
#import rpslam_mapping_v2
import time
import PiMotor
import gtpsim
import Navigation as nav


a1 = PiMotor.Arrow(1)
a2 = PiMotor.Arrow(2)
a3 = PiMotor.Arrow(3)
a4 = PiMotor.Arrow(4)
t0 = time.perf_counter()
t=0
connection=0
def led_1(a1,a2,a3,a4):
    a1.off()
    a2.on()
    a3.off()
    a4.on()
    return

def led_2(a1,a2,a3,a4):
    a1.on()
    a2.off()
    a3.on()
    a4.off()
    return


#import Ultrasonic_module
from datetime import datetime
Connectionloop=True
while Connectionloop:
    try:    
        
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        port=10000
        server_address = ('192.168.1.200', port)
        print('starting up on %s port %s' % server_address)
        sock.bind(server_address)


        # Listen for incoming connections
        sock.listen(1)


        while True:
            # Wait for a connection
            #print(sys.stderr, 'waiting for a connection')
            #t1=time.perf_counter()
            #t=t1-t0
            #if t>l_off:
            #    led_off()
            #    l_off+=2
            #elif t>l_on:
            #    led_on()
            #    l_on+=2
            print('waiting for a connection')
            connection, client_address = sock.accept()

            try:
                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    command = connection.recv(1024)
                    #print('received "%s"' % command)
                    cmd = pickle.loads(command)
                    cmd
                    #cmd = command.decode('UTF-8')
                    if cmd != '':
                        #cmd = int(cmd)
                        print('cmd = Recived')
                    else:    
                        #print('no more data from', client_address)
                        break
                    
                    
                    # Recording command
                    if (cmd[0] == 1):
                        print('Recording command')
                        recording_time = cmd[1]
                        recording_name = cmd[2]

                        #print('Recording')
                        connection.sendall(b'MU - Recording')
                        Recording.measure(recording_time, recording_name)

                        #print('Recording Complited')
                        connection.sendall(b'MU - Recording Completed')

                        with open(recording_name, 'rb') as f:
                          for l in f: connection.sendall(l)

                        break
                    


                    # Go to point command
                    if (cmd[0] == 2):
                        point_to_go = cmd[1]
                        time.sleep(20)
                        print('going to point command')
                    
                        connection.sendall(b'Going to point')
                        #Test_Motor.go_to_point(point_to_go)
                        #connection,sock=gtpsim.test(connection,sock)
                        Area, Height = nav.measurement_process(connection,sock)
                        break



                    # Mapping room command
                    if (cmd[0] == 3):
                        room_name = cmd[1]
                        map_date = cmd[2]
                        print('Mapping command')
                        #Sends back to SU message that 
                        connection.sendall(b'Scan will begin in 10 seconds please leave the room')
                        time.sleep(5)
                        for try_number in range(5):
                            try:                                
                                time.sleep(5)
                                basic_values,mapbytes=rpslam_mapping_v2.rpslam_map(connection, client_address)
                                scan_state=b'2'
                                break
                            except:
                                scan_status=(b'problem with scan, trying again in 5 seconds, try %d out of 5'%(try_number))
                                connection.sendall(scan_status)

                        basicvalues_filename="basicvalues_"+map_date+".p"
                        mapfile_name="mapbytes_"+map_date+".p"
                        #np.savetxt("basicvalues_"+date+".csv", [basic_values], delimiter=",")
                        time.sleep(1)
                        if try_number==5:
                            scan_state=b'1'
                            connection.sendall(scan_state)
                        else:
                            scan_state=b'2'
                            bv_send = pickle.dumps(basic_values)
                            #pickle.dumps( basic_values, open( basicvalues_filename, "wb" ) )
                            pickle.dump( mapbytes, open( mapfile_name, "wb" ) )
                            connection.sendall(scan_state)
                            time.sleep(2)
                            with open(mapfile_name, 'rb') as f:
                              for l in f: connection.sendall(l)
                            #time.sleep(2)
                            #with open(basicvalues_filename, 'rb') as f:
                            #  for l in f: connection.sendall(l)
                            #sock.sendall(bv_send)
                            break

                    # ULTRASONIC command
                    #if (cmd[0] == 4):
                    #    # ULTRASONIC MEASUREMENT
                    #    height_of_room = Ultrasonic_module.measure_height()
                    #    print(height_of_room)
                    #    data_height = pickle.dumps(height_of_room)
                    #    connection.sendall(data_height)
                    # Go to point command
                    if (cmd[0] == 5):
                        break
            
            except Exception as e:
                    print(e)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    connection.close()
            finally:
                # Clean up the connection
                connection.close()
    except Exception as e:
        print(e)
        print('reconnecting')
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        time.sleep(30)