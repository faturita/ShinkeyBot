import Configuration
import serial
import time
import datetime
from struct import *
import struct
import sys, os, select
import socket
import fcntl
from threading import Timer
import signal
import time
import subprocess

from connection import MCast
from SerialConnection import SerialConnection
from motor.MotorCortex import MotorCortex
from sensors.SensorimotorCortex import SensorimotorCortex

from Fps import Fps

# --- Disabling this for now, it was giving me some headaches
# First create a witness token to guarantee only one instance running
if (os.access("running.wt", os.R_OK)):
    print('Another instance is running. Cancelling.')
    quit(1)

runningtoken = open('running.wt', 'w')
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')

runningtoken.write(st)
runningtoken.close()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Initialize UDP Controller Server on port 10001 (BotController)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 10001)
print('Starting up Controller Server on '+server_address[0])
sock.bind(server_address)

if (Configuration.broadcast_IP):
    sock.setblocking(0)
    sock.settimeout(0.01)

noticer = MCast.Sender()

# Fixme push the network name inside the configuration file.
myip = get_ip_address('wlan0')

if (len(myip)>0):
    myip = myip
else:
    myip = 'None'

start = time.time()
print('Multicasting my own IP address: ' + myip)
while Configuration.broadcast_IP:
    noticer.send()
    try:
        data, address = sock.recvfrom(1)
        if (len(data) > 0):
            break
    except:
        data = None

    if (abs(time.time()- start) > 5):
        print('Giving up broadcasting ip... Lets get started.')
        break

def timeout():
    print ('Sending a multicast update of my own ip address:'+myip)
    noticer.send()

if (Configuration.broadcast_IP):
    sock.setblocking(1)
    sock.settimeout(0)


import platform
system_platform = platform.system()
if system_platform == "Darwin":
    import FFMPegStreamer as pcs
    portname='/dev/cu.usbmodem143101'
else:
    import H264Streamer as pcs
    portname = None

dosomestreaming = True

# Get PiCamera stream and read everything in another thread.
vst = pcs.H264VideoStreamer()
if (dosomestreaming):
    try:
        #vst.startAndConnect()
        vst.spanAndConnect()
        pass
    except Exception as e:
        print('Error starting H264 stream thread:'+str(e))

# Enables the sensor telemetry.  Arduinos will send telemetry data that will be
#  sent to listening servers.
sensesensor = False

class Surrogator:
    def __init__(self, sock):
        print ('Remote controlling ShinkeyBot')
        self.data = ''
        self.message = ''
        self.controlvalue = 0
        self.command = ''
        self.sock = sock
        self.address = None
        self.keeprunning = True

    def getdata(self):
        return self.data

    def getcommand(self):
        self.data = ''
        try:
            # Read from the UDP controller socket non blocking
            self.data, self.address = self.sock.recvfrom(1)
        except Exception:
            pass

    def getmessage(self):
        self.data = ''
        self.command = ''
        try:
            # Read from the UDP controller socket non blocking
            # The message format is AANNN
            self.message, self.address = self.sock.recvfrom(5)
            self.command = chr(int(self.message[0]))
            self.data = chr(int(self.message[1]))
            #print('Data', self.data)
            self.controlvalue = int(self.message[2:5])
        except Exception:
            pass


    def hookme(self):
        while (self.keeprunning):
            nextdata  = ''
            self.getcommand()

            if (self.data == 'X'):
                break

        print ('Stopping surrogate...')

sur = Surrogator(sock)

fps = Fps()
fps.tic()

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')

connection = SerialConnection(portname=portname)
motor = MotorCortex(connection = connection)
# Connect remotely to any client that is waiting for sensor loggers.
sensorimotor = SensorimotorCortex(connection,'sensorimotor',24)
sensorimotor.init()
sensorimotor.start()
sensorimotor.sensorlocalburst=1000
sensorimotor.sensorburst=100
sensorimotor.updatefreq=10
sensorimotor.cleanbuffer()

connection.send(b'AE010')
connection.send(b'AB100')

def terminate():
    print('Stopping ALPIBot')
    
    try:
        motor.stop()
    finally:
        os.remove('running.wt')

    print ('ALPIBot has stopped.')
    exit(0)

signal.signal(signal.SIGINT, lambda signum, frame: terminate())
signal.signal(signal.SIGTERM, lambda signum, frame: terminate())

print('ALPIBot ready.')
# Live
while(True):
    try:
        fps.steptoc()
        ts = int(time.time())
        #runninglog.write(str(ts) + ',' + str(fps.fps) + '\n')
        #print "Estimated frames per second: {0}".format(fps.fps)
        data = ''
        # TCP/IP server is configured as non-blocking
        sur.getmessage()

        cmd = sur.command
        cmd_data, address = sur.data, sur.address

        # If someone asked for it, send sensor information.
        if (sensesensor):
            sens = sensorimotor.picksensorsample()

            if (sens != None):
                # Check where to put the value
                sensorimotor.repack([10],[fps.fps])
                sensorimotor.send(sensorimotor.data)

        #if (cmd_data != ''):
        #    print(cmd)
        #    print(cmd_data)

        if (cmd == 'A'):
            if (len(sur.message)==5):
                # Sending the message that was received.
                print(sur.message)
                connection.send(sur.message)
                sur.message = ''

        elif (cmd == 'U'):
            # Activate/Deactivate sensor data.
            if (cmd_data == '!'):
                # IP Address exchange.
                sensorimotor.ip = address[0]
                sensorimotor.restart()

                print ("Reloading target ip for telemetry:"+sensorimotor.ip)          
            
            elif (cmd_data == 'Q'):
                sensesensor = True
            elif (cmd_data == 'q'):
                sensesensor = False

            if (cmd_data == 'K'):
                #Scan
                motor.connection.send(b'K')
            if (cmd_data == 'N'):
                motor.connection.send(b'H')
                #Camera Right
            elif (cmd_data == 'B'):
                motor.connection.send(b'G')
                #Camera Center
                visualpos = [90,95]
            elif (cmd_data == 'V'):
                motor.connection.send(b'F')
                #Camera Left
            elif (cmd_data == 'C'):
                motor.connection.send(b'T')
                #Camera nose down



            elif (cmd_data=='L'):
                motor.connection.send(b'L')
                motor.connection.send(b'L')
                # Laser on
            elif (cmd_data=='l'):
                motor.connection.send(b'l')
                motor.connection.send(b'l')
                # Laser off
            elif (cmd_data=='{'):
                # Camera left
                visualpos[0]=visualpos[0]+1;
                motor.connection.send(bytes('AF'+'{:3d}'.format(visualpos[0]),'ascii'))
            elif (cmd_data=='}'):
                # Camera right
                visualpos[0]=visualpos[0]-1;
                motor.connection.send(bytes('AF'+'{:3d}'.format(visualpos[0]),'ascii'))
            elif (cmd_data=='['):
                # Nose down
                visualpos[1]=visualpos[1]-1;
                motor.connection.send(bytes('AT'+'{:3d}'.format(visualpos[1]),'ascii'))
            elif (cmd_data==']'):
                # Nose up
                visualpos[1]=visualpos[1]+1;
                motor.connection.send(bytes('AT'+'{:3d}'.format(visualpos[1]),'ascii'))
            elif (cmd_data=='a'):
                # Scan right
                scan=scan-1;
                motor.connection.send(bytes('AO'+'{:3d}'.format(scan),'ascii'))
            elif (cmd_data=='d'):
                # Scan left
                scan=scan+1;
                motor.connection.send(bytes('AO'+'{:3d}'.format(scan),'ascii'))
            elif (cmd_data=='M'):
                pass
                #prop.moveto(mtrn, hidraw, tgt)
                # PID to desired position
            elif (cmd_data=='E'):
                motor.connection.send(b'E')
                # Empire song
            elif (cmd_data=='P'):
                motor.connection.send(b'B')

            elif (cmd_data == ' '):
                motor.stop()

            elif (cmd_data == 'w'):
                motor.move_forward()
            elif (cmd_data == 's'):
                motor.move_backwards()
            elif (cmd_data == 'd'):
                motor.move_right()
            elif (cmd_data == 'a'):
                motor.move_left()
            elif (cmd_data == '.'):
                motor.decrease_speed()
            elif (cmd_data == ','):
                motor.increase_speed()
            elif (cmd_data == 'X'):
                break
    except Exception as e:
        print ("Error:" + str(e))
        print ("Waiting for serial connection to reestablish...")
        connection.reconnect()

        # Instruct the Sensorimotor Cortex to stop wandering.
        sensorimotor.reset()

    sys.stdout.flush() # for service to print logs

vst.keeprunning = False
vst.interrupt()
sur.keeprunning = False

# When everything done, release the capture
sock.close()
terminate()
