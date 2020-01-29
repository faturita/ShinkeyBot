import serial
import time
import os

if (os.path.exists('/dev/cu.usbmodem144101')):
   mtrn = serial.Serial(port='/dev/cu.usbmodem144101',baudrate=9600,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   mtrn = serial.Serial(port='/dev/ttyACM1',baudrate=9600,timeout=0)

time.sleep(5)

buf = mtrn.read(25)

print (str(buf))

time.sleep(1)
mtrn.read(1000)
mtrn.write(b'A6080')
time.sleep(2)
mtrn.write(b'AA120')
time.sleep(2)
mtrn.read(11111)
mtrn.close()

