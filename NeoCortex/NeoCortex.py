#coding: latin-1

import numpy as np
import cv2

import serial

import time
from struct import *

import sys, os, select

import socket

import Proprioceptive as prop
import PicameraStreamer as pcs
import SensorimotorLogger as senso

obj = pcs.VideoStreamer()

import thread

thread.start_new_thread( obj.connect, () )


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

wristpos=48

sensesensor = 1

sensorimotor = senso.Sensorimotor()
sensorimotor.start()
sensorimotor.cleanbuffer(ssmr,mtrn)

while(True):
    try:
        data, address = sock.recvfrom(1)

        if (sensesensor == 1):
            sensorimotor.sendsensorsample(ssmr,mtrn)

        if (data == 'Y'):
            mtrn.write('A3250')
            time.sleep(0.8)
            mtrn.write('A5000')
        elif (data=='J'):
            # mtrn.write('A6180')
            wristpos = wristpos + 1
            mtrn.write('A6'+'{:3d}'.format(wristpos))
        elif (data=='j'):
            # mtrn.write('A6090')
            wristpos = wristpos - 1
            mtrn.write('A6'+'{:3d}'.format(wristpos))
        elif (data == 'H'):
            mtrn.write('A4250')
            time.sleep(0.2)
            mtrn.write('A5000')
        elif (data=='G'):
            mtrn.write('A1000')
            time.sleep(2)
        elif (data=='R'):
            mtrn.write('A1200')
            time.sleep(2)
        elif (data==' '):
            ssmr.write('1')
        elif (data=='W'):
            ssmr.write('2')
        elif (data=='S'):
            ssmr.write('3')
        elif (data=='D'):
            ssmr.write('5')
        elif (data=='A'):
            ssmr.write('4')
        elif (data=='.'):
            ssmr.write('-')
        elif (data==','):
            ssmr.write('+')
        elif (data=='L'):
            ssmr.write('L')
        elif (data=='l'):
            ssmr.write('l')
        elif (data=='+'):
            tgt = tgt + 100
        elif (data=='-'):
            tgt = tgt - 100
        elif (data=='T'):
            prop.moveto(mtrn, hidraw, tgt)
        elif (data=='X'):
            break
    except:
        print "Waiting for serial connection to reestablish..."
        time.sleep(2)
        ssmr.close()
        mtrn.close()
        [ssmr, mtrn] = prop.serialcomm()

        # Instruct the Sensorimotor Cortex to stop wandering.
        ssmr.write('C')

obj.keeprunning = False
time.sleep(2)

#When everything done, release the capture
mtrn.close()
ssmr.close()
sock.close()
