#coding: latin-1
import numpy as np
import cv2
import socket
import sys
import time
from connection import MCast
import os
import ConfigMe
import Configuration

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('Parameters:' + str(sys.argv))
# Fetch the remote ip if I do not have one.  It should be multicasted by ShinkeyBot
reporter = MCast.Receiver()

ConfigMe.createconfig("config.ini")

# Load the configuration file
lastip = ConfigMe.readconfig("config.ini")

print("Last ip used:"+lastip)

if (len(sys.argv)<2):
    print ("Waiting for Multicast Message")
    shinkeybotip = reporter.receive()
    print ('Bot IP:' + shinkeybotip)
    ip = shinkeybotip
elif sys.argv[1] == '-f':
    print ("Forcing IP Address")
    ip = lastip
else:
    ip = sys.argv[1]
    print ("Using IP:"+ip)

ConfigMe.setconfig("config.ini","ip",ip)
server_address = (ip, Configuration.controlport)

def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()

print('Press X to stop Bot')
print('Press x to exit this controller')
print('Press f to enter new update frequency for the bot.')

while (True):
  print ('>')
  data = getch()

  if (data.startswith('x')):
      sock.close()
      quit()

  if (data.startswith('f')):
      newfreq = input('Freq:');
      sent = sock.sendto(bytes('AE'+'{:3d}'.format(newfreq),'ascii'), server_address)
      sent = sock.sendto(bytes('AB'+'{:3d}'.format(1),'ascii'), server_address)
  elif (data.startswith('c')):
      print('Command:')
      cmd = sys.stdin.readline()
      sent = sock.sendto(bytes(cmd,'ascii'), server_address)
  else:
      sent = sock.sendto(bytes('U'+data+'000','ascii'), server_address)

  if (data.startswith('!')):
      print ("Letting know Bot that I want streaming....")

  if (data.startswith('X')):
      break

print ("Insisting....")
for i in range(1,100):
    sent = sock.sendto(bytes('U'+data+'000','ascii'), server_address)

sock.close()
