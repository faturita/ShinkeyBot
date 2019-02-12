#coding: latin-1

# struct sensortype
# {
# 0  double onYaw;     // +4
# 1  double onPitch;   // +4 = 8
# 2  double onRoll;    // +4 = 12
# 3  float T;          // +4 = 16
# 4  float P;          // +4 = 20
# 5  double light;     // +4 = 24
# 6  int yaw;          // +2 = 26
# 7  int pitch;        // +2 = 28
# 8  int roll;         // +2 = 30
# 9  int geoYaw;       // +2 = 32
# 10 int geoPitch;     // +2 = 34
# 11 int geoRoll;      // +2 = 36
# 12 int sound;        // +2 = 38
# 13 int freq;         // +2 = 40
# 14 int counter;      // +2 = 42
# 15 int distance;     // +2 = 44
#
# } sensor;

# struct sensortype {
# 16 int counter; // 2
# 17 int encoder; // 2
# 18 float cx;    // 4
# 19 float cy;    // 4
# 20 float cz;    // 4
# 21 float angle; // 4
# 22 int wrist;   // 2
# 23 int elbow;   // 2
# 24 int fps;     // 2
# } sensor; // 26

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
    def __init__(self, name, length, mapping):
        self.name = name
        self.keeprunning = True
        self.ip = Configuration.controllerip
        self.telemetryport = Configuration.telemetryport
        self.sensors = None
        self.data = None
        self.length = length
        self.mapping = mapping
        self.sensorlocalburst=10000
        self.sensorburst=1

    def start(self):
        # Sensor Recording
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        self.f = open('../data/sensor.'+self.name+'.'+st+'.dat', 'w')

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

        ser.write('AB'+'{:3d}'.format(self.sensorburst))
        # Reactive sensor information
        ser.write('S')


    def send(self,data):
        sent = self.sock.sendto(data, self.server_address)

    def picksensorsample(self, ser):
        # read  Embed this in a loop.
        self.counter=self.counter+1
        if (self.counter>self.sensorlocalburst):
            ser.write('P')
            ser.write('S')
            self.counter=0
        myByte = ser.read(1)
        if myByte == 'S':
          readcount = 0
          #data = readsomething(ser,44)
          self.data = readsomething(ser,self.length)
          myByte = readsomething(ser,1)
          if len(myByte) >= 1 and myByte == 'E':
              # is  a valid message struct
              #new_values = unpack('ffffffhhhhhhhhhh', data)
              new_values = unpack(self.mapping, self.data)
              print new_values
              self.sensors = new_values
              #self.f.write( str(new_values[0]) + ' ' + str(new_values[1]) + ' ' + str(new_values[2]) + ' ' + str(new_values[3]) + ' ' + str(new_values[4]) + ' ' + str(new_values[5]) + ' ' + str(new_values[6]) + ' ' + str(new_values[7]) + ' ' + str(new_values[8]) + ' ' + str(new_values[9]) + ' ' + str(new_values[10]) + ' ' + str(new_values[11]) + ' ' + str(new_values[12]) + ' ' +  str(new_values[13]) + ' ' + str(new_values[14]) + '\n')
              self.f.write(' '.join(map(str, new_values)) + '\n')
              return new_values

    def close(self):
        self.f.close()
        self.sock.close()

    def restart(self):
        self.close()
        self.start()

if __name__ == "__main__":
    [ssmr, mtrn] = prop.serialcomm('/dev/cu.usbmodem1421')

    # Weird, long values (4) should go first.
    #sensorimotor = Sensorimotor('motorneuron',26,'hhffffhhh')
    sensorimotor = Sensorimotor('sensorimotor',52,'ffffffhhhhhhhhhhhhhh')
    sensorimotor.ip = sys.argv[1]
    sensorimotor.start()
    sensorimotor.cleanbuffer(ssmr)


    while True:
        sens = sensorimotor.picksensorsample(ssmr)
        mots = None
        sensorimotor.sensorlocalburst=10000
        sensorimotor.sensorburst=10
        if (sens != None):
            sensorimotor.send(sensorimotor.data)
