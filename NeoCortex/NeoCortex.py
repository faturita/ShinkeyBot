#coding: latin-1

import numpy as np
import cv2

import serial

import serial
import time
from struct import *

import sys, os, select

import socket

import Proprioceptive as prop


# Initialize UDP Controller Server on port 10001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 10001)
print >> sys.stderr, 'Starting up Controller Server on %s port %s', server_address
sock.bind(server_address)

hidraw = prop.setupsensor()

[ssmr, mtrn] = prop.serialcomm()

# Instruct the Sensorimotor Cortex to stop wandering.
ssmr.write('C')

tgt = -1000

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
    elif (data=='+'):
        tgt = tgt + 100
    elif (data=='-'):
        tgt = tgt - 100
    elif (data=='T'):
        prop.moveto(mtrn, hidraw, tgt)
    elif (data=='X'):
        break


#When everything done, release the capture
mtrn.close()
ssmr.close()
sock.close()
