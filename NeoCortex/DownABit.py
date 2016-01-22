import serial
import time

ser = serial.Serial(port='/dev/tty.usbmodem1421',baudrate=115200,timeout=0)

time.sleep(5)

buf = ser.read(25)

print str(buf)
ser.write('A4250')
time.sleep(2)
ser.write('A5000')
ser.close()
