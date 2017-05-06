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

    def connect(self):
        print "Openning single-client H264 streaming server:"+self.videoport
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.framerate = 10
            camera.color_effects = (128,128)

            server_socket = socket.socket()
            server_socket.bind(('0.0.0.0', self.videoport))
            server_socket.listen(0)

            # Accept a single connection and make a file-like object out of it
            connection = server_socket.accept()[0].makefile('wb')
            try:
                camera.start_recording(connection, format='h264')
                camera.wait_recording(100000)
                camera.stop_recording()
            finally:
                connection.close()
                server_socket.close()


if __name__ == "__main__":
    vd = H264VideoStreamer()
    vd.connect()
