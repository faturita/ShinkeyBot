import serial
import time
import os

if (os.path.exists('/dev/cu.usbmodem144101')):
   ser = serial.Serial(port='/dev/cu.usbmodem144101',baudrate=9600,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   ser = serial.Serial(port='/dev/ttyACM1',baudrate=9600,timeout=0)

time.sleep(2)
print (ser.read(25))
ser.write(b'A6180')
#ser.write('A3200')
time.sleep(4)
ser.write(b'A3000')
ser.write(b'A6090')
time.sleep(2)
ser.write(b'A4200')
ser.write(b'A1200')
time.sleep(2)
ser.write(b'A4000')
ser.write(b'A2200')
time.sleep(2)
ser.write(b'A2000')
time.sleep(5)
print ('Test successful.')
ser.close()
