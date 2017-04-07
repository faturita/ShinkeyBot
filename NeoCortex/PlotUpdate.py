#coding: latin-1

# Run me with frameworkpython

import matplotlib.pyplot as plt
import numpy as np

import serial
import time
import datetime
from struct import *

import sys, select

import socket
import Configuration

serialconnected = False

if (not serialconnected):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('0.0.0.0', Configuration.telemetryport)
    print >> sys.stderr, 'starting up on %s port %s', server_address

    sock.bind(server_address)


def gimmesomething(ser):
    while True:
        line = ser.readline()
        if (len(line)>0):
            break
    return line


# Sensor Recording
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
f = open('../data/sensor.'+st+'.dat', 'w')


if (serialconnected):

    ser = serial.Serial(port='/dev/cu.usbmodem1421', baudrate=9600, timeout=0)

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

ax.axis([0, 500, -500, 1200])


plcounter = 0

plotx = []

while True:
  # read
  if (serialconnected):
      ser.write('S')
      ser.write('P')
      myByte = ser.read(1)
  else:
      myByte = 'S'

  if myByte == 'S':
      if (serialconnected):
         data = ser.read(42)
         myByte = ser.read(1)
      else:
         data, address = sock.recvfrom(46)
         myByte = 'E'

      if myByte == 'E':
          # is  a valid message struct
          new_values = unpack('ffffffhhhhhhhhhh', data)
          print str(new_values[9]) + '\t' + str(new_values[10]) + '\t' + str(new_values[11])
          f.write( str(new_values[12]) + ' ' + str(new_values[3]) + ' ' + str(new_values[5]) + '\n')

          x.append( float(new_values[9]))
          y.append( float(new_values[10]))
          z.append( float(new_values[11]))

          plotx.append( plcounter )

          line1.set_ydata(x)
          line2.set_ydata(y)
          line3.set_ydata(z)

          line1.set_xdata(plotx)
          line2.set_xdata(plotx)
          line3.set_xdata(plotx)

          fig.canvas.draw()
          plt.pause(0.0001)

          plcounter = plcounter+1

          if plcounter > 500:
              plcounter = 0
              plotx[:] = []
              x[:] = []
              y[:] = []
              z[:] = []


f.close()
ser.close()
