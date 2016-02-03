#coding: latin-1

import hid
import time

import PID

import serial


def setupsensor():
    for d in hid.enumerate(0, 0):
        keys = d.keys()
        keys.sort()
        for key in keys:
            print "%s : %s" % (key, d[key])
            print ""


    hidraw = hid.device(0x1b67, 0x0004)
    hidraw.open(0x1b67, 0x0004)

    buf = [0] * (32+1)

    #�           Rpt, GnS, Tgt, Size, Index LSB, Index MSB, Data
    #buf[0:7] = [0x00,0x00, 0x01, 0x01, 0x00,     0x01,      0x01]
    #hidraw.send_feature_report(buf)

    #�Blink 4 pulses
    hidraw.send_feature_report([0x00, 0x00, 0x00,0x01, 0x01, 0x00, 0x03])

    hidraw.get_feature_report(33,33)
    time.sleep(3)


    #�Fixed
    hidraw.send_feature_report([0x00, 0x00, 0x00,0x01, 0x00, 0x00, 0x02])

    hidraw.get_feature_report(33,33)
    time.sleep(3)

    #�Adjust report rate to max speed....
    hidraw.send_feature_report([0x00, 0x00, 0x00,0x02, 0x00, 0x00, 0x81, 0x00])

    hidraw.get_feature_report(33,33)
    time.sleep(3)

    #�Adjust sample rate to max speed....
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


f = open('sensor.dat', 'w')

ser = serial.Serial(port='/dev/tty.usbmodem1411',baudrate=115200, timeout=0)
hidraw = setupsensor()

P = 1.2
I = 1
D = 0.001
pid = PID.PID(P, I, D)

pid.SetPoint=4500
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

    ser.write(cmd)

ser.write('A5000')
f.close()
ser.close()
