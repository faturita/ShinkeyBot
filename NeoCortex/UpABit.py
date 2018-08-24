import serial
import time
import os

if (os.path.exists('/dev/tty.usbmodem1431')):
   ser = serial.Serial(port='/dev/tty.usbmodem1431',baudrate=9600,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   ser = serial.Serial(port='/dev/ttyACM1',baudrate=9600,timeout=0)

time.sleep(5)

buf = ser.read(25)

print str(buf)

# for spd in range(1,251):
#     cmd = 'A4'
#
#     val = cmd+('%03d' % spd)
#     print val
#     ser.write(val)

ser.write('AC135')
time.sleep(2)
ser.write('A7160')
ser.write('A6170')
time.sleep(6)

ser.write('A2225')
ser.write('L')
time.sleep(1)
ser.write('A8220')
time.sleep(6)
ser.write('AA080')
ser.write('l')
ser.write('A9220')
time.sleep(1)
ser.write('A1225')
time.sleep(6)
ser.write('=')
ser.write('AC150')
time.sleep(6)
ser.write('=')
time.sleep(6)
ser.close()
