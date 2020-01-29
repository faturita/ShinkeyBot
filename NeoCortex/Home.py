import serial
import time
import os

if (os.path.exists('/dev/cu.usbmodem144101')):
   ser = serial.Serial(port='/dev/cu.usbmodem144101',baudrate=9600,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   ser = serial.Serial(port='/dev/ttyACM1',baudrate=9600,timeout=0)

time.sleep(5)

buf = ser.read(25)

print (str(buf))

ser.write(b'=')
time.sleep(6)
ser.close()
