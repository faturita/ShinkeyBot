#coding: latin-1

# This program works in tandem with "ShowSensorData"
# This program will log all the information that can be seen with the other program

import hid
import time

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
hidraw.send_feature_report([0x00, 0x00, 0x00,0x02, 0x00, 0x00, 0x01, 0x00])

hidraw.get_feature_report(33,33)
time.sleep(3)

#�Adjust sample rate to max speed....
hidraw.send_feature_report([0x00, 0x00, 0x00,0x02, 0x01, 0x00, 0x01, 0x00])

hidraw.get_feature_report(33,33)
time.sleep(3)


f = open('sensor.dat', 'w')

while True:
  # read
  dat = hidraw.read(8)

  framenumber = (dat[1] << 8) + dat[0]
  acceleration = (dat[3] << 8) + dat[2]
  zenith = (dat[5] << 8) + dat[4]
  azimuth = (dat[7] << 8) + dat[6]

  print str(framenumber) + str(dat) + str(acceleration) + '-' + str(zenith) + ',' + str(azimuth)

  f.write( str(acceleration) + ' ' + str(zenith) + ' ' + str(azimuth) + '\n'  )

f.close()
