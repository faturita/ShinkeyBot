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

import SensorimotorLogger as sensor

import matplotlib.pyplot as plt
class Plotter:

    def __init__(self,rangeval,minval,maxval):
        # You probably won't need this if you're embedding things in a tkinter plot...
        import matplotlib.pyplot as plt
        plt.ion()

        self.x = []
        self.y = []
        self.z = []

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        self.line1, = self.ax.plot(self.x,'r', label='X') # Returns a tuple of line objects, thus the comma
        self.line2, = self.ax.plot(self.y,'g', label='Y')
        self.line3, = self.ax.plot(self.z,'b', label='Z')

        self.rangeval = rangeval
        self.ax.axis([0, rangeval, minval, maxval])
        self.plcounter = 0
        self.plotx = []

    def plotdata(self,new_values):
        # is  a valid message struct
        #print new_values

        self.x.append( float(new_values[0]))
        self.y.append( float(new_values[1]))
        self.z.append( float(new_values[2]))

        self.plotx.append( self.plcounter )

        self.line1.set_ydata(self.x)
        self.line2.set_ydata(self.y)
        self.line3.set_ydata(self.z)

        self.line1.set_xdata(self.plotx)
        self.line2.set_xdata(self.plotx)
        self.line3.set_xdata(self.plotx)

        self.fig.canvas.draw()
        plt.pause(0.0001)

        self.plcounter = self.plcounter+1

        if self.plcounter > self.rangeval:
          self.plcounter = 0
          self.plotx[:] = []
          self.x[:] = []
          self.y[:] = []
          self.z[:] = []


if __name__ == "__main__":
    #mtrn = serial.Serial(port='/dev/cu.usbserial-A5047ITL', baudrate=9600,timeout=0)
    plotter = Plotter(500,-100,210)
    #sensorimotor = sensor.Sensorimotor()
    #sensorimotor.start()
    #sensorimotor.cleanbuffer(mtrn)

    import PID
    import random

    random.seed()

    P = 1
    I = 1
    D = 0.001
    pid = PID.PID(P, I, D)

    pid.SetPoint=180
    pid.setSampleTime(0.001)

    feedback = 180
    pid.update(feedback)
    output = 0
    while True:
        feedback=feedback + random.uniform(-0.1,0.1)
        #a = a+ b*1
        pid.update(feedback)
        output = pid.output

        signal = (-output+feedback)+150

        if (signal < 100):
            signal = 100
        if (signal > 200):
            signal = 200



        if (signal > 150):
            #feedback = feedback - 0.1
            pass
        if (signal < 150):
            #feedback = feedback + 0.1
            pass

        print output

        if (True):
            plotter.plotdata( [feedback, output, signal])
