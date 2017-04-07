#coding: latin-1

# struct sensortype
# {
#   double onYaw;     // +4
#   double onPitch;   // +4 = 8
#   double onRoll;    // +4 = 12
#   float T;          // +4 = 16
#   float P;          // +4 = 20
#   double light;     // +4 = 24
#   int yaw;          // +2 = 26
#   int pitch;        // +2 = 28
#   int roll;         // +2 = 30
#   int geoYaw;       // +2 = 32
#   int geoPitch;     // +2 = 34
#   int geoRoll;      // +2 = 36
#   int sound;        // +2 = 38
#   int freq;         // +2 = 40
#   int counter;      // +2 = 42
#
# } sensor;

import serial
import time
import datetime
from struct import *
import os

import socket
import sys

import Proprioceptive as prop

import Configuration

def readsomething(ser, length):
    #data = smnr.read(38)
    data = ''

    while(len(data)<length):
        byte = ser.read(1)
        if (len(byte)>0):
            data = data + byte

    return data

def gimmesomething(ser):
    while True:
        line = ser.readline()
        if (len(line)>0):
            break
    return line


class Sensorimotor:
    def __init__(self):
        self.name = 'sensorimotor'
        self.keeprunning = True
        self.ip = Configuration.ip
        self.telemetryport = Configuration.telemetryport
        self.sensors = None

    def start(self):
        # Sensor Recording
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        self.f = open('../data/sensor.'+st+'.dat', 'w')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ip, self.telemetryport)
        self.counter = 0


    def cleanbuffer(self, ser):
        # Cancel sensor information.
        ser.write('X')
        time.sleep(6)

        # Ser should be configured in non-blocking mode.
        buf = ser.readline()
        print str(buf)

        buf = ser.readline()
        print str(buf)

        buf = ser.readline()
        print str(buf)

        # Reactive sensor information
        ser.write('S')


    def sendsensorsample(self, ser):
        # read  Embed this in a loop.
        self.counter=self.counter+1
        if (self.counter>100):
            ser.write('P')
            ser.write('S')
            self.counter=0
        myByte = ser.read(1)
        if myByte == 'S':
          readcount = 0
          data = readsomething(ser,44)
          myByte = readsomething(ser,1)
          if len(myByte) >= 1 and myByte == 'E':
              # is  a valid message struct
              new_values = unpack('ffffffhhhhhhhhhh', data)
              print new_values
              self.sensors = new_values
              sent = self.sock.sendto(data, self.server_address)
              #print str(new_values[6]) + ' ' + str(new_values[7]) + ' ' + str(new_values[8]) + '\n'
              #self.f.write( str(new_values[6]) + ' ' + str(new_values[7]) + ' ' + str(new_values[8]) + '\n')
              return new_values

    def close(self):
        self.f.close()
        self.sock.close()

    def restart(self):
        self.close()
        self.start()

if __name__ == "__main__":
    [smnr, mtrn] = prop.serialcomm()

    sensorimotor = Sensorimotor()
    sensorimotor.start()
    sensorimotor.cleanbuffer(smnr)

    while True:
        sensorimotor.sendsensorsample(smnr)
