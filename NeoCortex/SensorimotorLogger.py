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

def gimmesomething(ser):
    while True:
        line = ssmr.readline()
        if (len(line)>0):
            break
    return line


class Sensorimotor:
    def __init__(self):
        self.name = 'sensorimotor'
        self.keeprunning = True

    def start(self):
        # Sensor Recording
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        self.f = open('../data/sensor.'+st+'.dat', 'w')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (Configuration.ip, Configuration.telemetryport)


    def cleanbuffer(self, smnr, mtrn):
        # Cancel sensor information.
        ssmr.write('X')
        time.sleep(6)


        buf = ssmr.readline()
        print str(buf)

        buf = ssmr.readline()
        print str(buf)

        buf = ssmr.readline()
        print str(buf)

        # Reactive sensor information
        ssmr.write('S')

    def sendsensorsample(self, smnr, mtrn):
        # read  Embed this in a loop.
        ssmr.write('S')
        myByte = ssmr.read(1)
        if myByte == 'S':
          data = ssmr.read(32)
          myByte = ssmr.read(1)
          if myByte == 'E':
              # is  a valid message struct
              new_values = unpack('fffhhhhhhff', data)
              print new_values
              sent = self.sock.sendto(data, self.server_address)
              self.f.write( str(new_values[6]) + ' ' + str(new_values[7]) + ' ' + str(new_values[8]) + '\n')

    def close(self):
        self.f.close()

if __name__ == "__main__":
    [smnr, mtrn] = serialcomm()
    smnr.close()

    hidraw = setupsensor()

    moveto(mtrn, hidraw, 30)

    f.close()
    mtrn.close()

    [ssmr, mtrn] = prop.serialcomm()

    sensorimotor = Sensorimotor()
    sensorimotor.start()
    sensorimotor.cleanbuffer(smnr,mtrn)

    while True:
        sensorimotor.sendsensorsample(smnr,mtrn)

sensorimotor.close()
ssmr.close()
mtrn.close()
