#coding: latin-1

# NeoCortex is the core program to control ShinkeyBot
# It handles basic USB-Serial comm with other modules and handles
# the basic operation of ShinkeyBot
#
# x) Transmit TCP/IP images through CameraStreamer.
# x) Captures sensor data from SensorimotorLogger
# x) Handles output to motor unit and sensorimotor commands through Proprioceptive
# x) Receives high-level commands from ShinkeyBotController.

import numpy as np
import cv2

import serial

import time
from struct import *

import sys, os, select

import socket

import thread
import Proprioceptive as prop


# Open connection to tilt sensor.
hidraw = prop.setupsensor()
# Open serial connection to MotorUnit and Sensorimotor Arduinos.
#[ssmr, mtrn] = prop.serialcomm()

mtrn = serial.Serial(port='/dev/cu.usbmodem1421',timeout=0, baudrate=9600);

mtrn.read(250);

time.sleep(2)
mtrn.read(250)

#mtrn.write('A3250')
time.sleep(0.2) # This time depends on the weight
#mtrn.write('A3000')
mtrn.write('A6090')
time.sleep(0.5)
mtrn.write('A6180')
mtrn.write('AA160')
time.sleep(2)
mtrn.write('AA150')

tgt = 300
prop.moveto(mtrn, hidraw, tgt)

tgt = -200
prop.moveto(mtrn, hidraw, tgt)
