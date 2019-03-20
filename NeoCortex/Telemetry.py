#coding: latin-1

# Run me with frameworkpython

# This program receives telemetry information from ShinkeyBot in real time
# You only need to send the Q command and data will start flushing.

import matplotlib.pyplot as plt
import numpy as np

import serial
import time
import datetime
from struct import *

import sys, select

import socket
import Configuration

data1 = 1
data2 = 2
data3 = 3

if (len(sys.argv)>=2):
    print "Reading which data to shown"
    data1 = int(sys.argv[1])
    data2 = int(sys.argv[2])
    data3 = int(sys.argv[3])


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

ax.axis([0, 500, -10, 200])


plcounter = 0

plotx = []


counter = 0

length = 26
unpackcode = 'hhffffhhh'

length = 52
unpackcode='ffffffhhhhhhhhhhhhhh'

if (serialconnected):
   ser.write('A7180')

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
         data = ser.read(length) # 24
         myByte = ser.read(1)
      else:
         data, address = sock.recvfrom(length) # 44+26
         myByte = 'E'

      if myByte == 'E' and len(data)>0 and len(data) == length:
          # is  a valid message struct
          new_values = unpack(unpackcode,data)
          #new_values = unpack('ffffffhhhhhhhhhh'+'hhffffhhh',data)
          #new_values = unpack('ffffffhhhhhhhhhh', data)
          print str(new_values)
          #print str(new_values[1]) + '\t' + str(new_values[2]) + '\t' + str(new_values[3])
          f.write( str(new_values[data1]) + ' ' + str(new_values[data2]) + ' ' + str(new_values[data3]) + '\n')

          x.append( float(new_values[data1]))
          y.append( float(new_values[data2]))
          z.append( float(new_values[data3]))

          plotx.append( plcounter )

          line1.set_ydata(x)
          line2.set_ydata(y)
          line3.set_ydata(z)

          line1.set_xdata(plotx)
          line2.set_xdata(plotx)
          line3.set_xdata(plotx)

          fig.canvas.draw()
          plt.pause(0.00001)

          plcounter = plcounter+1

          if plcounter > 500:
              plcounter = 0
              plotx[:] = []
              x[:] = []
              y[:] = []
              z[:] = []


f.close()
if (serialconnected):
   ser.close()
print 'Everything successfully closed.'
