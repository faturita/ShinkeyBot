import serial
import time

if (os.path.exists('/dev/tty.usbmodem1411')):
   ser = serial.Serial(port='/dev/tty.usbmodem1411',baudrate=115200,timeout=0)
elif (os.path.exists('/dev/ttyACM1')):
   ser = serial.Serial(port='/dev/ttyACM1',baudrate=115200,timeout=0)
   
time.sleep(5)

buf = ser.read(25)

print str(buf)

# for spd in range(1,251):
#     cmd = 'A4'
#
#     val = cmd+('%03d' % spd)
#     print val
#     ser.write(val)

ser.write('A3200')
time.sleep(5)
ser.write('A5000')
ser.close()
