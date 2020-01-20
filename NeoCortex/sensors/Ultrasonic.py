try:
    import RPi.GPIO as GPIO
    test_environment = False
except (ImportError, RuntimeError):
    from sensors import GPIOMock as GPIO
    test_environment = True

if (test_environment):
    print('In test enviorment')

import time
import threading

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

_distance = -1
def distance():
    return _distance

def ultrasonic_sensor_thread(name):
    global _distance

    try: 
        print('Ultrasonic sensor thread')
        while True:
            # set Trigger to HIGH
            GPIO.output(GPIO_TRIGGER, True)
        
            # set Trigger after 0.01ms to LOW
            time.sleep(0.00001)
            GPIO.output(GPIO_TRIGGER, False)
        
            start_time = time.time()
            stop_time = time.time()
        
            while GPIO.input(GPIO_ECHO) == 0:
                start_time = time.time()
        
            while GPIO.input(GPIO_ECHO) == 1:
                stop_time = time.time()
        
            # time difference between start and arrival
            time_elapsed = stop_time - start_time
            # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            _distance = (time_elapsed * 34300) / 2

    finally: 
        GPIO.cleanup()
    

ut = threading.Thread(target=ultrasonic_sensor_thread, args=(1,))

def start():
    ut.start()
