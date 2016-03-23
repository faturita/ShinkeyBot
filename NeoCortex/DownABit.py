import serial
import time

import os


if (os.path.exists('/dev/tty.usbmodem1411')):
   ser = serial.Serial(port='/dev/tty.usbmodem1411',baudrate=115200,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   ser = serial.Serial(port='/dev/ttyACM0',baudrate=115200,timeout=0)

time.sleep(5)

buf = ser.read(25)

print str(buf)
ser.write('A4200')
time.sleep(0.4)
ser.write('A5000')
ser.close()
