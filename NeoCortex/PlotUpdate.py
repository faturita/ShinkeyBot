#coding: latin-1

import matplotlib.pyplot as plt
import numpy as np

import serial
import time
from struct import *

import sys, select


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

# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()

x = []
y = []
z = []

fig = plt.figure()
ax = fig.add_subplot(111)



line1, = ax.plot(x,'r', label='X') # Returns a tuple of line objects, thus the comma
line2, = ax.plot(y,'g', label='Y')
line3, = ax.plot(z,'b', label='Z')

ax.axis([0, 500, -500, 500])


plcounter = 0

plotx = []

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

          x.append( float(new_values[6]))
          y.append( float(new_values[7]))
          z.append( float(new_values[8]))

          plotx.append( plcounter )



          line1.set_ydata(x)
          line2.set_ydata(y)
          line3.set_ydata(z)

          line1.set_xdata(plotx)
          line2.set_xdata(plotx)
          line3.set_xdata(plotx)

          fig.canvas.draw()

          plcounter = plcounter+1

          if plcounter > 500:
              plcounter = 0
              plotx[:] = []
              x[:] = []
              y[:] = []
              z[:] = []


f.close()
ser.close()
