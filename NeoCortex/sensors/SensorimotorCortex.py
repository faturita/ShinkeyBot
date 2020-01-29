#coding: latin-1
import serial
import time
import datetime
from struct import *
import os

import socket
import sys

import Configuration


class SensorimotorCortex:
    def __init__(self, connection, name, length, mapping=''):
        self.connection = connection
        self.name = name
        self.keeprunning = True
        self.ip = '127.0.0.1'
        self.telemetryport = Configuration.telemetryport
        self.sensors = None
        self.data = None
        self.length = length
        self.mapping = mapping
        self.sensorlocalburst=1
        self.sensorburst=1
        self.updatefreq=1
        self.ztime = int(time.time())

    def start(self):
        # Sensor Recording
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        self.f = open('./data/sensor.'+self.name+'.'+st+'.dat', 'w')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ip, self.telemetryport)
        self.counter = 0

    def init(self):
        # Clean buffer
        self.connection.read(1000)

        # Send the command to obtain the length of the dataframe
        self.connection.send(b'AC000')
        time.sleep(2)
        leng = self.connection.readsomething(2) # Reading INT

        # Send the command to obtain the format of the dataframe
        datapack=unpack('h',leng)
        self.length = datapack[0]

        self.connection.send(b'AD000')
        time.sleep(3)
        self.mapping = self.connection.gimmesomething().decode('ascii')

        print ('Length:'+str(self.length))
        print ('Format:'+self.mapping)

    def stop(self):
        self.connection.send(b'A3010')
        self.connection.send(b'A3000')
        self.connection.send(b'A0000')


    def cleanbuffer(self):
        # Cancel sensor information.
        self.connection.send(b'X')
        time.sleep(6)

        # Ser should be configured in non-blocking mode.
        self.connection.read(1000)
        self.connection.flush()

        self.connection.send(bytes('AB'+'{:30d}'.format(self.sensorburst),'ascii'))
        self.connection.send(bytes('AE'+'{:30d}'.format(self.updatefreq),'ascii'))

        time.sleep(1)
        msg = self.connection.read(1000)
        print(msg)


    def log(self, mapping,data):
        new_values = unpack(mapping, data)
        ts = int(time.time())-self.ztime
        self.f.write(str(ts) + ' '+ ' '.join(map(str, new_values)) + '\n')

    def send(self,data):
        try:
            sent = self.sock.sendto(data, self.server_address)
        except Exception as e:
            print('Telemetry Error:'+str(e))
            # @FIXME: Do nothing right now but I think I should restart the socket.

    def repack(self,list_pos,list_values):
        new_values = unpack(self.mapping, self.data)
        new_values = list(new_values)

        # Update the structure with the values obtained from here.
        for i,x in enumerate(list_pos,0):
            new_values[x] = list_values[i]

        new_values = tuple(new_values)
        self.data = pack(self.mapping, *new_values)

    def picksensorsample(self):
        # read  Embed this in a loop.
        self.counter=self.counter+1
        if (self.counter>self.sensorlocalburst):
            self.connection.send(b'S')
            self.counter=0
        myByte = self.connection.read(1)
        #print(myByte)
        if (myByte == b'S'):
          readcount = 0
          #data = readsomething(ser,44)
          self.data = self.connection.readsomething(self.length)
          myByte = self.connection.readsomething(1)
          if len(myByte) >= 1 and myByte == b'E':
              # is  a valid message struct
              #new_values = unpack('ffffffhhhhhhhhhh', data)
              new_values = unpack(self.mapping, self.data)
              print (new_values)
              self.sensors = new_values
              return new_values

        return None

    def close(self):
        self.f.close()
        self.sock.close()
        self.connection.close()

    def restart(self):
        self.f.close()
        self.sock.close()
        self.start()

    def reset(self):
        self.connection.flush()
        self.cleanbuffer()


#sensorimotor = Sensorimotor('sensorimotor',66,'fffffffffffhhhhhhhhhhh')


