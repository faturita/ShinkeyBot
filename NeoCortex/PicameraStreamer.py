#coding: latin-1
# ShinkeyBot PiCamera streamer

# This program runs as a standalone thread and capture blocks of 640x480
# images with the Picamera, and send the data directly to the Controlling server.

# This allow to see what ShineyBot can see.

# Problems:
# x) Too slow ! Of course that is why H.264 exists.  So it must be implemented


# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

import thread

import socket
import sys

import Configuration as conf

class VideoStreamer:
	def __init__(self):
		self.name = 'streamer'
		self.keeprunning = True
		self.ip = conf.ip
		self.videoport = conf.videoport
		self.fps = 1

	def startAndConnect(self):
		try:
		   thread.start_new_thread( self.connect )
		except:
		   print "Error: unable to start thread"

	def connect(self):
		print "Connecting streaming to:"+self.ip
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		server_address = (self.ip, self.videoport)

		camera = None

		try:
			sock.connect(server_address)

			# initialize the camera and grab a reference to the raw camera capture
			camera = PiCamera()
			camera.resolution = (640, 480)
			camera.framerate = 32
            camera.color_effects = (128,128)
			rawCapture = PiRGBArray(camera, size=(640, 480))

			# allow the camera to warmup
			time.sleep(0.1)

			frm = 0
            start = time.time()

			# capture frames from the camera
			for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
				# grab the raw NumPy array representing the image, then initialize the timestamp
				# and occupied/unoccupied text
				image = frame.array
                print 'Capturing.'+str(frm)

				gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

				gray = cv2.flip(gray,0)
				gray = cv2.flip(gray,1)

				# End time
				end = time.time()
				# Time elapsed
				seconds = end - start
				#print "Time taken : {0} seconds".format(seconds)

				frm = frm + 1
				if (frm >= 256):
					# Calculate frames per second
					self.fps  = frm / seconds;
					print "Estimated frames per second : {0}".format(self.fps);
					frm = 0
					start = time.time()

				data = np.zeros((640), dtype=np.uint8)
				data[0] = data[1] = data[2] = data[3] = data[5] = 32
				sent = sock.sendto(data, server_address)

				# for i in range(1,480):
				#    data = gray[i,:]
				#    sent = sock.sendto(data, server_address)

				data = gray.reshape(640*480,1)
			   	sent = sock.sendto(data, server_address)


				#cv2.imshow("My Image", gray)

				if cv2.waitKey(1) & 0xFF == ord('q'):
				  break


				# clear the stream in preparation for the next frame
				rawCapture.truncate(0)

				if (self.keeprunning == False):
				  break

		except Exception as exc:
			print "Error:"+exc.message

		print "Closing Streaming"
		sock.close()
		if (camera):
			print "Picamera released..."
			camera.close()

if __name__ == "__main__":
   vd = VideoStreamer()
   vd.connect()
