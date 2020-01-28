#coding: latin-1
import numpy as np
import cv2

import socket

import time

from connection import MCast

import Configuration
import ConfigMe

import os

import datetime
from struct import unpack

import sys, select

from TelemetryDictionary import telemetrydirs

from SLAMComputing import SLAMComputer

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


print('Parameters:' + str(sys.argv))

ConfigMe.createconfig("config.ini")

# Load the configuration file
lastip = ConfigMe.readconfig("config.ini")

print("Last ip used:"+lastip)

if (len(sys.argv)<2):
    print ("Waiting for Multicast Message")
    # Fetch the remote ip if I do not have one.  It should be multicasted by ShinkeyBot
    reporter = MCast.Receiver()
    shinkeybotip = reporter.receive()
    print ('Bot IP:' + shinkeybotip)
    ip = shinkeybotip
elif sys.argv[1] == '-f':
    print ("Forcing IP Address")
    ip = lastip
else:
    ip = sys.argv[1]
    print ("Using IP:"+ip)

sockcmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ConfigMe.setconfig("config.ini","ip",ip)
server_address = (ip, Configuration.controlport)

socktelemetry = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
svaddress = ('0.0.0.0', Configuration.telemetryport)
print ('Starting up on %s port %s' % server_address)
socktelemetry.bind(svaddress)
#socktelemetry.setblocking(0)
#socktelemetry.settimeout(0.01)

length = 66
unpackcode = 'fffffffffffhhhhhhhhhhh'


def sendmulticommand(cmd,times):
    for i in range(1,times):
        sent = sockcmd.sendto(bytes(cmd,'ascii'), server_address)

# Let the Brainstem release the robot.
for i in range(1,100):
    sent = sockcmd.sendto(bytes('U 000','ascii'), server_address)

time.sleep(10)

for i in range(1,2):
    print('Letting know Bot that I want telemetry.')
    sent = sockcmd.sendto(bytes('U!000','ascii'), server_address)

# Activate sensor reading and telemetry sending.
sent = sockcmd.sendto(bytes('U'+'Q'+'000','ascii'), server_address)

print ('>')

state = 0
action = ''

# dst = [0,0,0]

# olddst = dst

# t = Asynctimer()
# t.set(5)
# delay=10

# sd = Asynctimer()
# sd.set(10)

# q = Queue.Queue()

s = SLAMComputer()

while (True):

    data, address = socktelemetry.recvfrom(length)
    myByte = 'E'
    if myByte == 'E' and len(data)>0 and len(data) == length:
        # is  a valid message struct
        new_values = unpack(unpackcode,data)
        #new_values = unpack('ffffffhhhhhhhhhh', data)
        print (str(new_values))


    # Analyze incoming data...
    data = ''

    distance = new_values[telemetrydirs['scanned']]
    angle = new_values[telemetrydirs['scan']]

    gYaw = new_values[telemetrydirs['geoYaw']]
    gPitch = new_values[telemetrydirs['geoPitch']]
    gRoll = new_values[telemetrydirs['geoRoll']]
    near = new_values[telemetrydirs['distance']]
    heading = new_values[telemetrydirs['geoHeading']]


    [state, action] = s.compute(state, new_values)

    print ('State %d Distance %d Angle %d - (%d, %d, %d)' % (state,near,heading, gYaw, gPitch, gRoll))


    if (len(action)>0):
        # Determine action command and send it.
        print(action)
        sent = sockcmd.sendto(bytes(action,'ascii'), server_address)

    if (data.startswith('!')):
      print ("Letting know Bot that I want streaming....")

    if (data.startswith('X')):
      break

print ("Insisting....")
for i in range(1,100):
    sent = sockcmd.sendto(bytes('U'+data+'000','ascii'), server_address)

sockcmd.close()
