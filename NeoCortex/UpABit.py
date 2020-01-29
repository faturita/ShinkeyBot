import serial
import time
import os

if (os.path.exists('/dev/cu.usbmodem144101')):
   ser = serial.Serial(port='/dev/cu.usbmodem144101',baudrate=9600,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   ser = serial.Serial(port='/dev/ttyACM1',baudrate=9600,timeout=0)

time.sleep(5)

buf = ser.read(25)

print (str(buf))

# for spd in range(1,251):
#     cmd = 'A4'
#
#     val = cmd+('%03d' % spd)
#     print val
#     ser.write(val)

ser.write(b'AC105')
time.sleep(2)
ser.write(b'A7160')
ser.write(b'A6170')
time.sleep(6)

ser.write(b'A2225')
ser.write(b'L')
time.sleep(1)
ser.write(b'A8220')
time.sleep(6)
ser.write(b'AA080')
ser.write(b'l')
ser.write(b'A9220')
time.sleep(1)
ser.write(b'A1225')
time.sleep(6)
ser.write(b'=')
ser.write(b'AC150')
time.sleep(6)
ser.write(b'=')
time.sleep(6)
ser.close()
