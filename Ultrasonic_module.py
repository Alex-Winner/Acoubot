import RPi.GPIO as GPIO
import time
import PiMotor

def measure_height(height_offset):
    GPIO.setwarnings(False)

    TRIG = 29
    ECHO = 31

    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
 
    avgDistance=0
    num_of_measurements = 50
    for i in range(num_of_measurements):
        GPIO.output(TRIG, False)
        time.sleep(0.1)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        while GPIO.input(ECHO)==0:
            pulse_start = time.time()

        while GPIO.input(ECHO)==1:
            pulse_end = time.time()
        
        pulse_duration = pulse_end - pulse_start

        distance = (pulse_duration * 343) / 2
        avgDistance = avgDistance + distance

    avgDistance = avgDistance / num_of_measurements + height_offset
    #print('Height = ' + str(round(measure_height() * 100, 2)) + ' cm')

    return avgDistance

a = measure_height()
print(a*100)
