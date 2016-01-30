#coding: latin-1

import numpy as np
import cv2

import serial

import serial
import time
from struct import *

import sys, select

import socket


# Initialize UDP Controller Server on port 10001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 10001)
print >> sys.stderr, 'Starting up Controller Server on %s port %s', server_address
sock.bind(server_address)


#window = namedWindow("TheWindow",1)
ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0)
smr = serial.Serial(port='/dev/ttyACM1', baudrate=115200, timeout=0)

serialport = 0
while (True):
    if (os.path.exists('/dev/ttyACM'+str(serialport))):
        ser = serial.Serial(port='/dev/ttyACM'+str(serialport), baudrate=115200, timeout=0)
        break
    serialport = serialport + 1

serialport = serialport + 1
while (True):
    if (os.path.exists('/dev/ttyACM'+str(serialport))):
        smr = serial.Serial(port='/dev/ttyACM'+str(serialport), baudrate=115200, timeout=0)
        break
    serialport = serialport + 1

time.sleep(5)

# Initialize connection with Arduino
idstring = ser.read(25)

if (idstring.startswith('Motor Unit Neuron')):
    mtrn = ser
    ssmr = smr
else:
    ssmr = smr
    mtrn = ser

ssmr.write('C')

while(True):
    data, address = sock.recvfrom(1)

    if (data == 'O'):
        mtrn.write('A3250')
        time.sleep(3)
        mtrn.write('A5000')
    elif (data == 'L'):
        mtrn.write('A4250')
        time.sleep(2)
        mtrn.write('A5000')
    elif (data=='G'):
        mtrn.write('A1000')
        time.sleep(2)
    elif (data=='R'):
        mtrn.write('A1200')
        time.sleep(2)
    elif (data=='W'):
        ssmr.write('2')
    elif (data=='S'):
        ssmr.write('3')
    elif (data=='D'):
        ssmr.write('5')
    elif (data=='A'):
        ssmr.write('4')
    elif (data=='X'):
        break


#When everything done, release the capture
ser.close()
smr.close()
sock.close()
