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

from Fps import Fps

import SensorimotorLogger as Senso

if __name__ == "__main__":
    [ssmr, mtrn] = prop.serialcomm()

    # Weird, long values (4) should go first.
    #sensorimotor = Sensorimotor('motorneuron',26,'hhffffhhh')
    sensorimotor = Senso.Sensorimotor('sensorimotor',16,'fffhh')
    sensorimotor.sensorlocalburst=100
    sensorimotor.sensorburst=10
    sensorimotor.updatefreq=10
    sensorimotor.ip = sys.argv[1]
    sensorimotor.start()
    sensorimotor.init(ssmr)
    print (sensorimotor.mapping)
    print (sensorimotor.length)
    sensorimotor.cleanbuffer(ssmr)

    fps = Fps()
    fps.tic()

    while True:
        fps.steptoc()
        sens = sensorimotor.picksensorsample(ssmr)
        mots = None
        if (sens != None):
            sensorimotor.repack([0],[fps.fps])
            sensorimotor.send(sensorimotor.data)
