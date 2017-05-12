#coding: latin-1

import socket
import time
import picamera
import thread

import Configuration as conf

class H264VideoStreamer:
    def __init__(self):
        self.name = 'streamer'
        self.keeprunning = True
        self.ip = conf.shinkeybotip
        self.videoport = conf.videoport
        self.fps = 1
        self.thread = None

    def interrupt(self):
        print 'Interrupting stream h264 server...'
        self.thread.exit()

    def startAndConnect(self):
        try:
            self.thread = thread.start_new_thread( self.connect, () )
        except Exception as e:
            print "Error:" + e.message
            print "Error: unable to start thread"

    def connectMe(self, server_socket):
        print "Openning single-client H264 streaming server:"+str(self.videoport)
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 10
            camera.hflip = True
            camera.vflip = True
            camera.color_effects = (128,128)

            # Accept a single connection and make a file-like object out of it
            socketconnection = server_socket.accept()
            connection = socketconnection[0].makefile('wb')
            try:
                camera.start_recording(connection, format='h264')
                camera.wait_recording(100000)
                camera.stop_recording()
            finally:
                try:
                    socketconnection.close()
                    sleep(2)
                    camera.close()
                    print 'Connection closed.'
                except:
                    server_socket.close()

    def connect(self):
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', self.videoport))
        server_socket.listen(1)


if __name__ == "__main__":
    doWait = True
    while(doWait):

        try:
            vd = H264VideoStreamer()
            vd.connect()
            doWait = False
        except KeyboardInterrupt:
            doWait = False
        except:
            print 'error!!'
            doWait=True
