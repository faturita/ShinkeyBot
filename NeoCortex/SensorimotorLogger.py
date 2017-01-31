#coding: latin-1

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
        smnr.write('S')

    def sendsensorsample(self, ser):
        # read  Embed this in a loop.
        self.counter=self.counter+1
        if (self.counter>500):
            ser.write('P')
            ser.write('S')
            self.counter=0
        myByte = ser.read(1)
        if myByte == 'S':
          readcount = 0
          data = readsomething(ser,38)
          myByte = readsomething(ser,1)
          if len(myByte) >= 1 and myByte == 'E':
              # is  a valid message struct
              new_values = unpack('ffffffhhhhhhh', data)
              print new_values
              sent = self.sock.sendto(data, self.server_address)
              self.f.write( str(new_values[6]) + ' ' + str(new_values[7]) + ' ' + str(new_values[8]) + '\n')
              return new_values

    def close(self):
        self.f.close()
        self.sock.close()

if __name__ == "__main__":
    [smnr, mtrn] = prop.serialcomm()

    sensorimotor = Sensorimotor()
    sensorimotor.start()
    sensorimotor.cleanbuffer(smnr)

    while True:
        sensorimotor.sendsensorsample(smnr)
