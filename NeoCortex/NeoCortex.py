#coding: latin-1
import numpy as np
import cv2

import socket

import time

import MCast

import Configuration
import ConfigMe

import os

import datetime
from struct import *

import sys, select

import Queue

class Cmd:
    def __init__(self,cmd,dl):
        self.cmd = cmd
        self.delay = dl

class Asynctimer:
    def set(self,delay):
        self.delay = delay
        self.counter = 0
    def check(self):
        self.counter = self.counter + 1
        if (self.counter>self.delay):
            return True
        else:
            return False


socktelemetry = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
svaddress = ('0.0.0.0', Configuration.telemetryport)
print >> sys.stderr, 'starting up on %s port %s', svaddress

socktelemetry.bind(svaddress)
#socktelemetry.setblocking(0)
#socktelemetry.settimeout(0.01)

length = 52
unpackcode = 'ffffffhhhhhhhhhhhhhh'

sockcmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

lastip = ConfigMe.readconfig("config.ini")
server_address = (lastip, Configuration.controlport)

def sendmulticommand(cmd,times):
    for i in range(1,times):
        sent = sockcmd.sendto(cmd, server_address)

# Let the Brainstem release the robot.
for i in range(1,100):
    sent = sockcmd.sendto(' ', server_address)

time.sleep(10)

for i in range(1,2):
    print('Letting know Bot that I want telemetry.')
    sent = sockcmd.sendto('U!000', server_address)

sent = sockcmd.sendto('UQ000', server_address)

print '>'

state = 0

dst = [0,0,0]

olddst = dst

t = Asynctimer()
t.set(5)
delay=10

sd = Asynctimer()
sd.set(10)

q = Queue.Queue()


state = 0

while (True):

    data, address = socktelemetry.recvfrom(length)
    myByte = 'E'
    if myByte == 'E' and len(data)>0 and len(data) == length:
        # is  a valid message struct
        new_values = unpack(unpackcode,data)
        #new_values = unpack('ffffffhhhhhhhhhh', data)
        print str(new_values)


    # Analyze incoming data...
    data = ''

    distance = new_values[19]
    angle = new_values[18]

    gYaw = new_values[9]
    gPitch = new_values[10]
    gRoll = new_values[11]

    near = new_values[15]

    print (distance)
    print (angle)

    #print (str(gYaw) + '-' + str(gPitch) + '-' + str(gRoll))


    if (angle<30 and distance>0 and state==2):
        dst[0] = distance
        state = 3
    elif ((angle>=79 and angle<=90) and distance>0 and state==4):
        dst[1] = distance
        state = 5
    elif (angle>115 and distance>0 and state==6):
        dst[2] = distance
        state =7

    print (dst)
    print (near)

    if (near < 30 and state ==0):
        data = 'U 000'
        state = 1

    if (state == 0):
        data = 'UW000'

    if (sd.check()):
        # Firing check command
        print ('Firing check command')
        sd.set(2)
        if (state == 1):
            data = 'AO010'
            state = 2
            sd.set(15)
        elif (state == 3):
            data = 'AO090'
            state = 4
            sd.set(15)
        elif (state == 5):
            data = 'AO170'
            state = 6
            sd.set(15)
        elif (state == 7):
            dirval = max(dst)
            dir = dst.index(dirval)
            if (dir==2):
                data = 'UA000'
            elif (dir==0):
                data = 'UD000'
            else:
                data = 'UW000'
            state = 0
            sd.set(2)

    else:
        data = 'UO000'


    if (len(data)>0 and t.check()):
        # Determine action command and send it.
        print data
        sent = sockcmd.sendto(data, server_address)

    if (data.startswith('!')):
      print "Letting know Bot that I want streaming...."

    if (data.startswith('X')):
      break

print "Insisting...."
for i in range(1,100):
    sent = sockcmd.sendto(data, server_address)

sock.close()
