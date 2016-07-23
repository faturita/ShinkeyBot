#coding: latin-1
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
# 15 is the pitch
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 100)
pwm.start(5)

class App:

    # tower pro microservo in te turret it is from 3-26 13-26
    def update(self, angle):
        duty = float(angle) * 23/180.0 + 2
        pwm.ChangeDutyCycle(duty)

d = App()

try:  
    # here you put your main loop or block of code  
    #for i in range(1,180):
    #   d.update(i)
    #   time.sleep(0.01)
     

    d.update(90)
    time.sleep(5)
    d.update(180)
    time.sleep(2)
    d.update(3)

     
    print "Signal sent....Waiting"
    time.sleep(5)

except KeyboardInterrupt:  
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    print "\n", counter # print value of counter  
  
except:  
    # this catches ALL other exceptions including errors.  
    # You won't get any error messages for debugging  
    # so only use it once your code is working  
    print "Other error or exception occurred!"  
  
finally:  
    GPIO.cleanup() # this ensures a clean exit 


