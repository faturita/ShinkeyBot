#coding: latin-1
import numpy as np
import cv2

import socket
import sys

import time

import MCast

import ConfigParser
import io

import os

def setconfig(configfile_name,option,value):
    with open(configfile_name) as f:
        sample_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(sample_config))

    cfgfile = open(configfile_name, 'w')
    config.set('server', option, value)
    config.write(cfgfile)
    cfgfile.close()

def readconfig(configfile_name):
    with open(configfile_name) as f:
        sample_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(sample_config))

    #print("List all contents")
    for section in config.sections():
        #print("Section: %s" % section)
        for options in config.options(section):
            #print("x %s:::%s:::%s" % (options,
            #                  config.get(section, options),
            #                  str(type(options))))
            if (options == 'ip'):
                return config.get(section, options)

def createconfig(configfile_name):
    # Check if there is already a configurtion file
    if not os.path.isfile(configfile_name):
        # Create the configuration file as it doesn't exist yet
        cfgfile = open(configfile_name, 'w')

        # Add content to the file
        Config = ConfigParser.ConfigParser()
        Config.add_section('server')
        Config.set('server', 'ip', '10.17.66.164')
        Config.add_section('other')
        Config.set('other', 'use_anonymous', True)
        Config.write(cfgfile)
        cfgfile.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#server_address = ('192.168.0.110', 10001)
#server_address = ('10.16.23.142', 10001)

# Fetch the remote ip if I do not have one.  It should be multicasted by ShinkeyBot
reporter = MCast.Receiver()

print sys.argv

createconfig("config.ini")

# Load the configuration file
lastip = readconfig("config.ini")

print("Last ip used:"+lastip)

if (len(sys.argv)<2):
    print "Waiting for Multicast Message"
    shinkeybotip = reporter.receive()
    print 'Bot IP:' + shinkeybotip
    ip = shinkeybotip
elif sys.argv[1] == '-f':
    print "Forcing IP Address"
    ip = '192.168.0.110'
else:
    ip = sys.argv[1]
    print "Using IP:"+ip

setconfig("config.ini","ip",ip)
server_address = (ip, 10001)

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

while (True):
  print '>'
  data = getch()

  sent = sock.sendto(data, server_address)

  if (data.startswith('!')):
      print "Letting know Bot that I want streaming...."

  if (data.startswith('X')):
      break

print "Insisting...."
for i in range(1,100):
    sent = sock.sendto(data, server_address)

sock.close()
