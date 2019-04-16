#coding: latin-1
#sensorimotor = Sensorimotor('sensorimotor',66,'fffffffffffhhhhhhhhhhh')

import serial
import time
import datetime
from struct import *
import os

import socket
import sys

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
        self.sensorlocalburst=1
        self.sensorburst=1
        self.updatefeq=1
        self.ztime = int(time.time())

    def start(self):
        # Sensor Recording
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        self.f = open('../data/sensor.'+self.name+'.'+st+'.dat', 'w')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ip, self.telemetryport)
        self.counter = 0


    def init(self, ser):
        # Clean buffer
        ser.read(1000)

        ser.write('AC'+'000')
        time.sleep(2)
        leng = readsomething(ser,2) # Reading INT

        datapack=unpack('h',leng)
        self.length = datapack[0]

        ser.write('AD'+'000')
        time.sleep(3)
        self.mapping = gimmesomething(ser)


    def cleanbuffer(self, ser):
        # Cancel sensor information.
        ser.write('X')
        time.sleep(6)

        # Ser should be configured in non-blocking mode.
        ser.read(1000)

        ser.write('AB'+'{:3d}'.format(self.sensorburst))
        ser.write('AE'+'{:3d}'.format(self.updatefreq))
        # Reactive sensor information
        ser.write('S')


    def log(self, mapping,data):
        new_values = unpack(mapping, data)
        ts = int(time.time())-self.ztime
        self.f.write(str(ts) + ' '+ ' '.join(map(str, new_values)) + '\n')

    def send(self,data):
        sent = self.sock.sendto(data, self.server_address)

    def repack(self,list_pos,list_values):
        new_values = unpack(self.mapping, self.data)
        new_values = list(new_values)

        # Update the structure with the values obtained from here.
        for i,x in enumerate(list_pos,0):
            new_values[x] = list_values[i]

        new_values = tuple(new_values)
        self.data = pack(self.mapping, *new_values)

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
              return new_values

        return None

    def close(self):
        self.f.close()
        self.sock.close()

    def restart(self):
        self.close()
        self.start()
