#coding: latin-1

import serial
import time
import datetime
from struct import *
import os

import socket
import sys

import Proprioceptive as prop

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

import Configuration

server_address = (Configuration.ip, 10000)


def gimmesomething(ser):
    while True:
        line = ser.readline()
        if (len(line)>0):
            break
    return line


[ssmr, mtrn] = prop.serialcomm()

# Sensor Recording
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
f = open('../data/sensor.'+st+'.dat', 'w')

# Cancel sensor information.
ser.write('X')
time.sleep(6)


buf = ser.readline()
print str(buf)

buf = ser.readline()
print str(buf)

buf = ser.readline()
print str(buf)

# Reactive sensor information
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
          sent = sock.sendto(data, server_address)
          f.write( str(new_values[6]) + ' ' + str(new_values[7]) + ' ' + str(new_values[8]) + '\n')

f.close()
ser.close()
