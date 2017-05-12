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
                time.sleep(5)
                camera.stop_recording()
            finally:
                try:
                    camera.close()
                    print 'Camera closed'
                    time.sleep(2)
                    connection.flush()
                    socketconnection.close()
                    time.sleep(2)
                    print 'Connection closed.'
                except:
                    pass

    def connect(self):
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', self.videoport))
        server_socket.listen(1)

        doWait = True
        while(doWait):
            print 'Trying to reconnect....'
            time.sleep(5)
            try:
                self.connectMe(server_socket)
                doWait = False
            except KeyboardInterrupt:
                doWait = False
            except:
                print 'error!!'
                doWait=True


if __name__ == "__main__":
    vd = H264VideoStreamer()
    vd.connect()
