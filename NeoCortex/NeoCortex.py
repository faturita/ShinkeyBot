#coding: latin-1

# NeoCortex is the core program to control ShinkeyBot
# It handles basic USB-Serial comm with other modules and handles
# the basic operation of ShinkeyBot
#
# x) Transmit TCP/IP images through CameraStreamer.
# x) Captures sensor data from SensorimotorLogger
# x) Handles output to motor unit and sensorimotor commands through Proprioceptive
# x) Receives high-level commands from ShinkeyBotController.

import numpy as np
import cv2

import serial

import time
from struct import *

import sys, os, select

import socket

import Proprioceptive as prop
import thread
import PicameraStreamer as pcs
import SensorimotorLogger as senso
import MCast

# Ok, so the first thing to do is to broadcast my own IP address.

# Get PiCamera stream and read everything in another thread.
obj = pcs.VideoStreamer()
try:
    thread.start_new_thread( obj.connect, () )
    pass
except:
    pass



# Initialize UDP Controller Server on port 10001
# This receives high-level commands from ShinkeyBotController.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 10001)
print >> sys.stderr, 'Starting up Controller Server on %s port %s', server_address
sock.bind(server_address)

sock.setblocking(0)
sock.settimeout(5.0)

noticer = MCast.Sender()

myip = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
myip = myip[0]

# Shinkeybot truly does nothing until it gets the remote controlling connection
print 'Multicasting my own IP address:' + myip
while True:
    noticer.send()
    try:
        data, address = sock.recvfrom(1)
        if (len(data)>0):
            break
    except:
        data = None

# Open connection to tilt sensor.
hidraw = prop.setupsensor()
# Open serial connection to MotorUnit and Sensorimotor Arduinos.
[ssmr, mtrn] = prop.serialcomm()

# Instruct the Sensorimotor Cortex to stop wandering.
ssmr.write('C')

tgt = -300
wristpos=48

elbowpos = 150

# Pan and tilt
visualpos = [90,95]

sensesensor = 0

# Connect remotely to any client that is waiting for sensor loggers.
sensorimotor = senso.Sensorimotor()
sensorimotor.start()
sensorimotor.cleanbuffer(ssmr,mtrn)


print 'Remote controlling ShinkeyBot'
# Live
while(True):
    try:
        data, address = sock.recvfrom(1)

        # If someone asked for it, send sensor information.
        if (sensesensor == 1):
            sensorimotor.sendsensorsample(ssmr,mtrn)

        if (data == '!'):
            moredata, address = sock.recvfrom(4)
            obj.ip = str(moredata[0]) + '.' + str(moredata[1]) + '.' + str(moredata[2]) + '.' + str(moredata[3])

            try:
                thread.start_new_thread( obj.connect(), () )
            except:
                pass

        if (data == 'N'):
            ssmr.write('H')
            #Camera Right
        elif (data == 'B'):
            ssmr.write('G')
            #Camera Center
            visualpos = [90,95]
        elif (data == 'V'):
            ssmr.write('F')
            #Camera Left
        elif (data == 'C'):
            ssmr.write('T')
            #Camera nose down
        elif (data == 'Y'):
            # Move shoulder up
            mtrn.write('A3250')
            time.sleep(0.5) # This time depends on the weight
            mtrn.write('A3000')
        elif (data == 'H'):
            # Move shoulder down.
            mtrn.write('A4250')
            time.sleep(0.2)
            mtrn.write('A4000')
        elif (data=='<'):
            # Move elbows up (by increasing its torque)
            elbowpos = elbowpos + 1
            mtrn.write('AA'+'{:3d}'.format(elbowpos))
        elif (data=='>'):
            # Move elbows dow (by decreasing its torque)
            elbowpos = elbowpos - 1
            mtrn.write('AA'+'{:3d}'.format(elbowpos))
        elif (data=='Z'):
            # Reset Elbow position (no force)
            elbowpos = 150
            mtrn.write('AA'+'{:3d}'.format(elbowpos))
        elif (data=='J'):
            # mtrn.write('A6180')
            wristpos = wristpos + 1
            mtrn.write('A6'+'{:3d}'.format(wristpos))
            # wrist Up
        elif (data=='j'):
            # mtrn.write('A6090')
            wristpos = wristpos - 1
            mtrn.write('A6'+'{:3d}'.format(wristpos))
            # wrist down
        elif (data=='\''):
            mtrn.write('A8120')
            time.sleep(0.6)
            mtrn.write('A8000')
        elif (data=='?'):
            mtrn.write('A9120')
            time.sleep(0.6)
            mtrn.write('A9000')
        elif (data=='G'):
            # Grip close
            mtrn.write('A1200')
            time.sleep(2)
            mtrn.write('A1000')
        elif (data=='R'):
            # Grip open
            mtrn.write('A2200')
            time.sleep(2)
            mtrn.write('A2000')
            # Gripper Release
        elif (data==' '):
            ssmr.write('1')
            # Quiet
        elif (data=='W'):
            ssmr.write('2')
            # Forward
        elif (data=='S'):
            ssmr.write('3')
            # Backward
        elif (data=='D'):
            ssmr.write('4')
            # Right
        elif (data=='A'):
            ssmr.write('5')
            # Left
        elif (data=='.'):
            ssmr.write('-')
            # Move slowly
        elif (data==','):
            ssmr.write('+')
            # Move coarsely
        elif (data=='L'):
            ssmr.write('L')
            # Laser on
        elif (data=='l'):
            ssmr.write('l')
            # Laser off
        elif (data=='+'):
            tgt = tgt + 100
            # Pull up tesaki target
        elif (data=='-'):
            tgt = tgt - 100
            # Pull down tesaki target
        elif (data=='{'):
            visualpos[0]=visualpos[0]+1;
            ssmr.write('AF'+'{:3d}'.format(visualpos[0]))
        elif (data=='}'):
            visualpos[0]=visualpos[0]-1;
            ssmr.write('AF'+'{:3d}'.format(visualpos[0]))
        elif (data=='['):
            visualpos[1]=visualpos[1]-1;
            ssmr.write('AT'+'{:3d}'.format(visualpos[1]))
        elif (data==']'):
            visualpos[1]=visualpos[1]+1;
            ssmr.write('AT'+'{:3d}'.format(visualpos[1]))
        elif (data=='M'):
            prop.moveto(mtrn, hidraw, tgt)
            # PID to desired position
        elif (data=='E'):
            ssmr.write('E')
            # Empire song
        elif (data=='B'):
            ssmr.write('B')
            # Buzz
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
