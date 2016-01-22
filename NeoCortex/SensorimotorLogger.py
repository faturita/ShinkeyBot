#coding: latin-1

import serial
import time
from struct import *

def gimmesomething(ser):
    while True:
        line = ser.readline()
        if (len(line)>0):
            break
    return line


ser = serial.Serial(port='/dev/tty.usbmodem1411', baudrate=115200, timeout=0)

f = open('sensor.dat', 'w')


ser.write('X')
time.sleep(6)



buf = ser.readline()
print str(buf)

buf = ser.readline()
print str(buf)

buf = ser.readline()
print str(buf)

ser.write('S')


while True:
  # read
  myByte = ser.read(1)
  if myByte == 'S':
      data = ser.read(32)
      myByte = ser.read(1)
      if myByte == 'E':
          # is  a valid message struct
          new_values = unpack('fffhhhhhhff', data)
          print new_values
          f.write( str(new_values[6]) + ' ' + str(new_values[7]) + ' ' + str(new_values[8]) + '\n')

f.close()
ser.close()
