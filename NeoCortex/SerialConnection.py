import time
import serial
import datetime
import os

import datetime

baudrate = 9600

TRIES = 10

class SerialConnection(object): 
  def __init__(self, *, portname=None):
    self.connect(portname)

  def connect(self, portname=None):
    self.open = False
    self.ssmr = None
    self.myportname = portname
    tries = 0
    while (tries < TRIES):
      try:
        print('Opening port:'+str(portname)+'. Try '+str(tries + 1))
        [self.ssmr, self.mtrn] = self.serialcomm(serialportname=portname, tmtout=0)
        self.open = True
        print('Opened port '+str(self.ssmr))
        break
      except Exception as e: 
        print ('Error while establishing serial connection:' + str(e))
        tries += 1
    
    if (not self.open):
      print('Could not open serial port. Mocking serial...')

  def serialcomm(self,serialportname=None, tmtout=0):
      serialport = 0
      sera = None
      serb = None

      if (serialportname):
          sera = serial.Serial(port=serialportname, baudrate=baudrate,timeout=tmtout)
      if (sera == None):
          while (serialport<15):
              if (os.path.exists('/dev/ttyACM'+str(serialport))):
                  sera = serial.Serial(port='/dev/ttyACM'+str(serialport), baudrate=baudrate, timeout=tmtout)
                  break
              serialport = serialport + 1

          serialport = serialport + 1
          while (serialport<15):
              if (os.path.exists('/dev/ttyACM'+str(serialport))):
                  serb = serial.Serial(port='/dev/ttyACM'+str(serialport), baudrate=baudrate, timeout=tmtout)
                  break
              serialport = serialport + 1

      time.sleep(5)

      if (sera == None and serb != None):
          return [serb, sera]
      elif (sera != None and serb == None):
          return [sera, serb]

      # Initialize connection with Arduino
      idstring = sera.read(1000)
      if (serb):
          idstring = serb.read(1000)

      for tries in range(1, 10):
          sera.write('I')
          time.sleep(1)
          idstring = sera.read(100)

          if ('SSMR' in idstring):
              mrn = serb
              smr = sera
              print('Sensorimotor,Motorneuron detected.')
              return [smr, mrn]
          elif ('MTRN' in idstring):
              smr = serb
              mrn = sera
              print('Motornneuron,Sensorimotor detected.')
              return [smr, mrn]

      print ('Did not find serial')
      return [None, None]

  def send(self, data):
    if (self.open):
      #print(data)
      self.ssmr.write(data)
    else:
      print('Warning: serial port not open.')

  def read(self, length):
    if (self.open):
      return self.ssmr.read(length)
    else:
      print('Warning: serial port not open.')
      return None
    
  # There could be a chance that whatever is behind the serial connection get stuck
  # and do not reply anything.  Hence I need a way to break this up (that is what trials is for)
  def readsomething(self, length):
    data = b''
    trials = 10000000

    while(len(data)<length and trials>0):
        byte = self.ssmr.read(1)
        #print(byte)
        trials = trials - 1
        if (len(byte)>0):
            data =  b''.join([data, byte])

    return data

  def gimmesomething(self):
    while True:
        line = self.ssmr.readline()
        if (len(line)>0):
            break
    return line    

  def flush(self):
    self.ssmr.flush()
    self.ssmr.flushInput()
    self.ssmr.flushOutput()

  def close(self):
    if (not self.ssmr == None):
      self.ssmr.close()

  def reconnect(self):
    self.flush()
    self.close()
    self.connect(self.myportname)