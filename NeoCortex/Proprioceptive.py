#coding: latin-1

import hid
import time

import PID
import os
import serial

import datetime


def serialcomm():
    serialport = 0
    while (serialport<15):
        if (os.path.exists('/dev/ttyACM'+str(serialport))):
            sera = serial.Serial(port='/dev/ttyACM'+str(serialport), baudrate=115200, timeout=0)
            break
        serialport = serialport + 1

    serialport = serialport + 1
    while (serialport<15):
        if (os.path.exists('/dev/ttyACM'+str(serialport))):
            serb = serial.Serial(port='/dev/ttyACM'+str(serialport), baudrate=115200, timeout=0)
            break
        serialport = serialport + 1

    time.sleep(5)

    if (sera.isOpen() == False or serb.isOpen() == False):
        return [None, None]

    # Initialize connection with Arduino
    idstring = sera.read(250)

    for tries in range(1, 10):
        sera.write('I')
        time.sleep(1)
        idstring = sera.read(100)
    
        if ('SSMR' in idstring):
            mrn = serb
            smr = sera
            print('Sensorimotor detected.')
            return [smr, mrn]
        elif ('MTRN' in idstring):
            smr = serb
            mrn = sera
            print('Motornneuron detected.')
            return [smr, mrn]

    print ('Did not find serial')
    return [None, None]


def setupsensor():
    for d in hid.enumerate(0, 0):
        keys = d.keys()
        keys.sort()
        for key in keys:
            print "%s : %s" % (key, d[key])
            print ""


    hidraw = hid.device(0x1b67, 0x0004)
    hidraw.open(0x1b67, 0x0004)

    # Size of Feature Report is 33 bytes for Oak Sensors.
    buf = [0] * (32+1)

    #�           Rpt, GnS, Tgt, Size, Index LSB, Index MSB, Data
    #buf[0:7] = [0x00,0x00, 0x01, 0x01, 0x00,     0x01,      0x01]
    #hidraw.send_feature_report(buf)

    #�Blink 4 pulses
    hidraw.send_feature_report([0x00, 0x00, 0x00,0x01, 0x01, 0x00, 0x03])

    hidraw.get_feature_report(33,33)
    time.sleep(3)

    # Fixed
    hidraw.send_feature_report([0x00, 0x00, 0x00,0x01, 0x00, 0x00, 0x02])

    hidraw.get_feature_report(33,33)
    time.sleep(3)

    # Adjust report rate to max speed....
    hidraw.send_feature_report([0x00, 0x00, 0x00,0x02, 0x00, 0x00, 0x81, 0x00])

    hidraw.get_feature_report(33,33)
    time.sleep(3)

    # Adjust sample rate to max speed....
    hidraw.send_feature_report([0x00, 0x00, 0x00,0x02, 0x01, 0x00, 0x01, 0x00])

    hidraw.get_feature_report(33,33)
    time.sleep(3)

    return hidraw

def tiltsensor(hidraw):
    dat = hidraw.read(8)

    framenumber = (dat[1] << 8) + dat[0]
    acceleration = (dat[3] << 8) + dat[2]
    zenith = (dat[5] << 8) + dat[4]
    azimuth = (dat[7] << 8) + dat[6]

    return [acceleration, zenith, azimuth]

def moveto(mtrn, hidraw, targetpos):
    P = 1.2
    I = 1
    D = 0.001
    pid = PID.PID(P, I, D)

    pid.SetPoint=targetpos
    pid.setSampleTime(0.001)

    feedback = 0
    output = 0

    for i in range(1,100):
        [acceleration, zenith, azimuth ] = tiltsensor(hidraw)

        print str(acceleration) + '-' + str(zenith) + ',' + str(azimuth)

        f.write( str(acceleration) + ' ' + str(zenith) + ' ' + str(output) + '\n'  )

        feedback = float( zenith )

        if (azimuth < 25000):
            feedback = feedback * -1

        pid.update(feedback)
        output = pid.output

        cmd = 1

        if ( abs(output) < 10):
            cmd = 'A5000'
        elif ( output < 0):
            cmd = 'A4200'
        else:
            cmd = 'A3250'
        print str(output) + '-' + str(feedback) + ':' + cmd

        mtrn.write(cmd)

    # Stop moving
    mtrn.write('A5000')

class PIDTarget:
    def __init__(self):
       self.name = 'streamer'
       self.keeprunning = True

       self.P = 1.2
       self.I = 1
       self.D = 0.001
       self.pid = PID.PID(P, I, D)

       self.pid.SetPoint=targetpos
       self.pid.setSampleTime(0.001)

       self.feedback = 0
       self.output = 0

       self.i = 1

    def moveto(self, mtrn, hidraw, targetpos):
       if (i<=60):
            i=i+1

            [acceleration, zenith, azimuth ] = tiltsensor(hidraw)

            print str(acceleration) + '-' + str(zenith) + ',' + str(azimuth)

            f.write( str(acceleration) + ' ' + str(zenith) + ' ' + str(self.output) + '\n'  )

            self.feedback = float( zenith )

            if (azimuth < 25000):
                self.feedback = self.feedback * -1

            self.pid.update(self.feedback)
            self.output = self.pid.output

            cmd = 1

            if ( abs(self.output) < 10):
                cmd = 'A5000'
            elif ( self.output < 0):
                cmd = 'A4200'
            else:
                cmd = 'A3250'
            print str(self.output) + '-' + str(self.feedback) + ':' + cmd

            mtrn.write(cmd)

       # Stop moving
       mtrn.write('A5000')

# NavData Recording
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
f = open('../data/navdata'+st+'.dat', 'w')


def __init__(self):
    [smnr, mtrn] = serialcomm()
    smnr.close()

    hidraw = setupsensor()

    moveto(mtrn, hidraw, 30)

    f.close()
    mtrn.close()
