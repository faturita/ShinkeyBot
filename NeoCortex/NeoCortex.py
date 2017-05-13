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
import datetime
from struct import *

import sys, os, select

import socket

import Proprioceptive as prop
import thread
#import PicameraStreamer as pcs
import H264Streamer as pcs
import SensorimotorLogger as senso
import MCast

import fcntl
import struct

# First create a witness token to guarantee only one instance running
if (os.access("running.wt", os.R_OK)):
    print >> sys.stderr, 'Another instance is running. Cancelling.'
    quit(1)

runningtoken = open('running.wt', 'w')
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')

runningtoken.write(st)
runningtoken.close()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


# Get PiCamera stream and read everything in another thread.
vst = pcs.H264VideoStreamer()
try:
    vst.startAndConnect()
    pass
except:
    pass

# Ok, so the first thing to do is to broadcast my own IP address.
dobroadcastip = True

# Initialize UDP Controller Server on port 10001 (ShinkeyBotController)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 10001)
print >> sys.stderr, 'Starting up Controller Server on %s port %s', server_address
sock.bind(server_address)

if (dobroadcastip):
    sock.setblocking(0)
    sock.settimeout(0.01)

noticer = MCast.Sender()

# Fixme push the network name inside the configuration file.
myip = get_ip_address('wlan0')

if (len(myip)>0):
    myip = myip
else:
    myip = 'None'

# Shinkeybot truly does nothing until it gets connected to ShinkeyBotController
whenistarted = time.time()
print 'Multicasting my own IP address:' + myip
while dobroadcastip:
    noticer.send()
    try:
        data, address = sock.recvfrom(1)
        if (len(data)>0):
            break
    except:
        data = None

    if (abs(time.time()-whenistarted)>60):
        print 'Giving up broadcasting ip... Lets get started.'
        break

from threading import Timer

def timeout():
    print 'Sending a multicast update of my own ip address:'+myip
    noticer.send()

t = Timer(5 * 60, timeout)
t.start()

if (dobroadcastip):
    sock.setblocking(1)
    sock.settimeout(0)

print 'Connection to Remote Controller established.'

# Open connection to tilt sensor (@deprecated)
#hidraw = prop.setupsensor()
# Open serial connection to MotorUnit and Sensorimotor Arduinos.
[ssmr, mtrn] = prop.serialcomm()

# Instruct the Sensorimotor Cortex to stop wandering.
ssmr.write('C')

tgt = -300
wristpos=48

elbowpos = 90

shoulderpos = 150

# Pan and tilt
visualpos = [90,95]

# Enables the sensor telemetry.  Arduinos will send telemetry data that will be
#  sent to listening servers.
sensesensor = True

# Connect remotely to any client that is waiting for sensor loggers.
sensorimotor = senso.Sensorimotor('sensorimotor',44,'ffffffhhhhhhhhhh')
sensorimotor.start()
sensorimotor.cleanbuffer(ssmr)

if (mtrn):
    motorneuron = senso.Sensorimotor('motorneuron',26,'hhffffhhh')
    motorneuron.start()
    motorneuron.cleanbuffer(mtrn)


class Surrogator:
    def __init__(self, sock):
        print 'Remote controlling ShinkeyBot'
        self.data = ''
        self.sock = sock
        self.address = None
        self.keeprunning = True

    def getdata(self):
        return self.data

    def getcommand(self):
        self.data = ''
        try:
            # Read from the UDP controller socket non blocking
            self.data, self.address = self.sock.recvfrom(1)
        except Exception as e:
            pass


    def hookme(self):
        while (self.keeprunning):
            nextdata  = ''
            self.getcommand()

            if (self.data == 'X'):
                break

        print 'Stopping surrogate...'

sur = Surrogator(sock)

#try:
#    thread.start_new_thread( sur.hookme, () )
#    pass
#except:
#    pass

target = [0,0,0]
automode = False;

# Live
while(True):
    try:
        data = ''
        # TCP/IP server is configured as non-blocking
        sur.getcommand()
        data, address = sur.data, sur.address

        # If someone asked for it, send sensor information.
        if (sensesensor):
            sens = sensorimotor.picksensorsample(ssmr)
            mots = motorneuron.picksensorsample(mtrn)

            if (sens != None and mots != None):
                sensorimotor.send(sens)
                sensorimotor.send(mots)

            if (sens != None and target != None):
                if (target[0] == 0):
                    target = sens[9], sens[10], sens[11]

                if (automode):
                    #print "Moving to :" + str(target[0]) + '\t' + str(target[1]) + '\t' + str(target[2])
                    #print "From:     :" + str(sens[9])   + '\t' + str(sens[10])  + '\t' + str(sens[11])
                    #if (not ( abs(sens[9]-target[0])<10) ):
                    #    ssmr.write('-')
                    #    ssmr.write('4')
                    #    time.sleep(0.2)
                    #    ssmr.write('5')
                    #    time.sleep(0.1)

                    print 'Auto:Sensing distance:'+str(sens[15])
                    ssmr.write('+')
                    ssmr.write('2')
                    if (sens[15]<90):
                        ssmr.write('5')


        if (data == '!'):
            # IP Address exchange.
            sensorimotor.ip = address[0]
            sensorimotor.restart()

            motorneuron.ip = address[0]
            motorneuron.restart()

            print "Reloading target ip for telemetry:"+sensorimotor.ip

            # Vst VideoStream should be likely restarted in order to check
            # if something else can be enabled.


        if (data == 'Q'):
            # Activate/Deactivate sensor data.
            sensesensor = (not sensesensor)
        if (data == 'K'):
            # Automode
            automode = (not automode)
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
            shoulderpos = shoulderpos + 1
            mtrn.write('A7'+'{:3d}'.format(shoulderpos))
        elif (data == 'H'):
            # Move shoulder down.
            shoulderpos = shoulderpos - 1
            mtrn.write('A7'+'{:3d}'.format(shoulderpos))
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
            elbowpos = 90
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
            # Wrist clockwise
            mtrn.write('A8120')
        elif (data=='?'):
            # Wrist anticlockwise
            mtrn.write('A9120')
        elif (data=='G'):
            # Grip close
            mtrn.write('A1220')
        elif (data=='R'):
            # Grip open
            mtrn.write('A2200')
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
            mtrn.write('L')
            ssmr.write('L')
            # Laser on
        elif (data=='l'):
            mtrn.write('l')
            ssmr.write('l')
            # Laser off
        elif (data=='+'):
            tgt = tgt + 100
            # Pull up tesaki target
        elif (data=='-'):
            tgt = tgt - 100
            # Pull down tesaki target
        elif (data=='{'):
            # Camera left
            visualpos[0]=visualpos[0]+1;
            ssmr.write('AF'+'{:3d}'.format(visualpos[0]))
        elif (data=='}'):
            # Camera right
            visualpos[0]=visualpos[0]-1;
            ssmr.write('AF'+'{:3d}'.format(visualpos[0]))
        elif (data=='['):
            # Nose down
            visualpos[1]=visualpos[1]-1;
            ssmr.write('AT'+'{:3d}'.format(visualpos[1]))
        elif (data==']'):
            # Nose up
            visualpos[1]=visualpos[1]+1;
            ssmr.write('AT'+'{:3d}'.format(visualpos[1]))
        elif (data=='M'):
            pass
            #prop.moveto(mtrn, hidraw, tgt)
            # PID to desired position
        elif (data=='E'):
            ssmr.write('E')
            # Empire song
        elif (data=='P'):
            ssmr.write('B')
            # Buzz
        elif (data=='X'):
            break
    except Exception as e:
        print "Error:" + e.message
        print "Waiting for serial connection to reestablish..."
        if (not ssmr == None):
            ssmr.close()
        if (not mtrn == None):
            mtrn.close()
        [ssmr, mtrn] = prop.serialcomm()

        # Instruct the Sensorimotor Cortex to stop wandering.
        ssmr.write('C')

vst.keeprunning = False
sur.keeprunning = False
time.sleep(2)


#When everything done, release the capture
if (not ssmr == None):
    ssmr.close()
sock.close()
if (not mtrn == None):
    mtrn.close()

try:
    t.cancel()
    print 'Thread successfully closed.'
except Exception as e:
    print 'Exception while closing video stream thread.'
    traceback.print_exc(file=sys.stdout)

os.remove('running.wt')
print 'ShinkeyBot has stopped.'
