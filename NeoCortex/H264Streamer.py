#coding: latin-1

import socket
import time
import picamera
import threading
import subprocess
import os
import signal

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

        if (self.pro):
            os.killpg(os.getpgid(self.pro.pid), signal.SIGTERM)  
            print('Killing process')

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('127.0.0.1', self.videoport)
            sock.connect(server_address)
            sock.send(b'1')
            sock.close()
        except Exception as e:
            print('Streaming Server seems to be down:' + str(e))


    def spanAndConnect(self):
        try:
            FNULL = open(os.devnull, 'w')
            self.pro = subprocess.Popen(['/usr/bin/python3', 'H264Streamer.py'],preexec_fn=os.setsid)
            if self.pro.stderr or self.pro.returncode:
                return False
        except Exception as e:
            print ("Error:" + str(e))
            print ("Error: unable to start a new thread")

    def startAndConnect(self):
        try:
            self.thread = threading.Thread(target=self.connect, args=(1,))
            self.thread.start()
        except Exception as e:
            print ("Error:" + str(e))
            print ("Error: unable to start a new thread")

    def connectMe(self, server_socket):
        print ("Openning single-client H264 streaming server:"+str(self.videoport))
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
                    print ('Camera closed')
                    time.sleep(2)
                    connection.flush()
                    socketconnection.close()
                    time.sleep(2)
                    print ('Connection closed.')
                except:
                    pass

    def connect(self, name):
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', self.videoport))
        server_socket.listen(1)

        doWait = True
        while(doWait and self.keeprunning):
            print ('Restablishing Connection...')
            time.sleep(5)
            try:
                self.connectMe(server_socket)
                doWait = False
            except KeyboardInterrupt:
                doWait = False
            except Exception as e:
                print ('Exception:'+str(e))
                doWait=True

        server_socket.close()


if __name__ == "__main__":
    vd = H264VideoStreamer()
    vd.startAndConnect()

    input()
