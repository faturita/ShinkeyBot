import serial
import time
import os

if (os.path.exists('/dev/tty.usbmodem1431')):
   ser = serial.Serial(port='/dev/tty.usbmodem1431',baudrate=9600,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   ser = serial.Serial(port='/dev/ttyACM1',baudrate=9600,timeout=0)

time.sleep(5)

buf = ser.read(25)

print str(buf)


ser.write('AC100')
time.sleep(2)
ser.write('A7210')
ser.write('AA070')
ser.write('A6180')
time.sleep(5)

ser.write('A2225')
ser.write('L')
time.sleep(2)
ser.write('AA060')
ser.write('l')
time.sleep(1)
ser.write('A1225')
time.sleep(4)
ser.write('A7150')
time.sleep(2)
ser.write('=')
ser.write('AC150')
time.sleep(4)
ser.write('=')
time.sleep(3)
ser.close()
