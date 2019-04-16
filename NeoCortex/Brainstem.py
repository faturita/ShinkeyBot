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

from Fps import Fps

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


# Open connection to tilt sensor (@deprecated)
#hidraw = prop.setupsensor()
# Open serial connection to MotorUnit and Sensorimotor Arduinos.
def doserial():
    retries=1
    ssmr=None
    mtrn=None
    while (retries<5):
        try:
            [ssmr, mtrn] = prop.serialcomm()
            print 'Connection established'
            return [ssmr, mtrn]
        except Exception as e:
            print 'Error while establishing serial connection.'
            retries=retries+1

    return [ssmr, mtrn]

[ssmr, mtrn] = doserial()

# Instruct the Sensorimotor Cortex to stop wandering.
ssmr.write('C')
ssmr.write('B')
time.sleep(1)
ssmr.write('B')

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


def terminateme():
    try:
        t.cancel()
        print 'Thread successfully closed.'
    except Exception as e:
        print 'Exception while closing video stream thread.'
        traceback.print_exc(file=sys.stdout)

    os.remove('running.wt')
    print 'ShinkeyBot has stopped.'


if (ssmr == None and mtrn == None):
    terminateme()


tgt = -300

wristpos=90
elbowpos = 90
shoulderpos = 150
pitpos = 150

# Pan and tilt
visualpos = [90,95]

scan = 90

# Enables the sensor telemetry.  Arduinos will send telemetry data that will be
#  sent to listening servers.
sensesensor = False

# Connect remotely to any client that is waiting for sensor loggers.
sensorimotor = senso.Sensorimotor('sensorimotor',66,'fffffffffffhhhhhhhhhhh')
sensorimotor.start()
sensorimotor.init(ssmr)
sensorimotor.sensorlocalburst=100
sensorimotor.sensorburst=10
sensorimotor.updatefreq=10
sensorimotor.cleanbuffer(ssmr)

if (mtrn):
    motorneuron = senso.Sensorimotor('motorneuron',26,'hhffffhhh')
    motorneuron.start()
    sensorimotor.init(mtrn)
    motorneuron.cleanbuffer(mtrn)


class Surrogator:
    def __init__(self, sock):
        print 'Remote controlling ShinkeyBot'
        self.data = ''
        self.message = ''
        self.controlvalue = 0
        self.command = ''
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

    def getmessage(self):
        self.data = ''
        try:
            # Read from the UDP controller socket non blocking
            # The message format is AANNN
            self.message, self.address = self.sock.recvfrom(5)
            self.command = self.message[0]
            self.data = self.message[1]
            self.controlvalue = int(self.message[2:5])
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

target = [0,1,0]
automode = False;

fps = Fps()
fps.tic()

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
runninglog = open('../data/brainstem.'+st+'.dat', 'w')

# Live
while(True):
    try:
        fps.steptoc()
        ts = int(time.time())
        runninglog.write(str(ts) + ',' + str(fps.fps) + '\n')
        #print "Estimated frames per second: {0}".format(fps.fps)
        data = ''
        # TCP/IP server is configured as non-blocking
        sur.getmessage()
        data, address = sur.data, sur.address

        # If someone asked for it, send sensor information.
        if (sensesensor):
            sens = sensorimotor.picksensorsample(ssmr)
            mots = None

            if (mtrn):
                mots = motorneuron.picksensorsample(mtrn)

            if (sens != None and mots != None):
                sensorimotor.repack([0],[fps.fps])
                sensorimotor.send(sensorimotor.data+motorneuron.data)

            if (sens != None):
                sensorimotor.repack([0],[fps.fps])
                sensorimotor.send(sensorimotor.data)

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
        if (sur.command == 'A'):
            if (len(sur.message)==5):
                # Sending the message that was received.
                ssmr.write(sur.message)
                sur.message = ''

        elif (sur.command == 'U'):

            if (data == '!'):
                # IP Address exchange.
                sensorimotor.ip = address[0]
                sensorimotor.restart()

                if (mtrn):
                    motorneuron.ip = address[0]
                    motorneuron.restart()

                print "Reloading target ip for telemetry:"+sensorimotor.ip

                # Vst VideoStream should be likely restarted in order to check
                # if something else can be enabled.


            if (data == 'Q'):
                # Activate/Deactivate sensor data.
                sensesensor = True
            elif (data == 'q'):
                sensesensor = False
            if (data == 'K'):
                #Scan
                ssmr.write('K')
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
            elif (data == '='):
                #Home position.
                mtrn.write('=')
                wristpos=90
                elbowpos=90
                pitpos = 150
                shoulderpos=150
            elif (data == '$'):
                pitpos = pitpos + 1
                mtrn.write('AC'+'{:3d}'.format(pitpos))
            elif (data == '%'):
                pitpos = pitpos - 1
                mtrn.write('AC'+'{:3d}'.format(pitpos))
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
            elif (data=='a'):
                # Scan right
                scan=scan-1;
                ssmr.write('AO'+'{:3d}'.format(scan))
            elif (data=='d'):
                # Scan left
                scan=scan+1;
                ssmr.write('AO'+'{:3d}'.format(scan))
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
            elif (data=='('):
                sensorimotor.sensorlocalburst = 100
            elif (data==')'):
                sensorimotor.sensorlocalburst = 10000
            elif (data=='O'):
                ssmr.write('O')
            elif (data=='X'):
                break
    except Exception as e:
        print "Error:" + e.message
        print "Waiting for serial connection to reestablish..."
        if (not ssmr == None):
            ssmr.close()
        if (not mtrn == None):
            mtrn.close()
        [ssmr, mtrn] = doserial()

        # Instruct the Sensorimotor Cortex to stop wandering.
        if (ssmr != None):
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

terminateme()
