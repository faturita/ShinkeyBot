#coding: latin-1
#
#
# FFMPEG Streamer
#
# This class can act as a thread receiving TCP/IP connections on the specified
# port and start to transmit the video streaming information
#

import socket
import time
import subprocess
import os
import signal
import threading

import Configuration as conf

class H264VideoStreamer:
    def __init__(self):
        self.name = 'streamer'
        self.keeprunning = True
        self.videoport = conf.videoport
        self.fps = 1
        self.thread = None
        self.pro = None

    def interrupt(self):
        print ('Interrupting stream h264 server...')
        os.killpg(os.getpgid(self.pro.pid), signal.SIGTERM) 
        

    def startAndConnect(self):
        try:
            self.thread = threading.Thread(target=self.connect, args=(1,))

        except Exception as e:
            print ("Error:" + e)
            print ("Error: unable to start thread")

    def connectMe(self):
        print ("Openning single-client H264 streaming server:"+str(self.videoport))

        FNULL = open(os.devnull, 'w')
        self.pro = subprocess.Popen(['ffmpeg', '-f','avfoundation','-framerate','20','-video_size','640x480','-i','0:none','-tune','zerolatency','-pix_fmt','yuv422p','-f','mpegts','udp://localhost:10000'],preexec_fn=os.setsid,stdout=FNULL,stderr=FNULL)
        if self.pro.stderr or self.pro.returncode:
            return False

    def close(self):
        self.keeprunning = False
        self.interrupt()

    def connect(self):

        doWait = True
        while(doWait):
            print ('Restablishing Connection...')
            time.sleep(5)
            try:
                self.connectMe()
                doWait = False
            except KeyboardInterrupt:
                doWait = False
            except Exception as e:
                print ('Error:'+ str(e))
                doWait=True


if __name__ == "__main__":
    vd = H264VideoStreamer()
    vd.connect()
    time.sleep(20)
    vd.interrupt()
    time.sleep(5)
