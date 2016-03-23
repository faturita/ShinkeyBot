# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.0.109', 10000)

sock.connect(server_address)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

frm = 0

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	gray = cv2.flip(gray,0)
	gray = cv2.flip(gray,1)

	frm = frm + 1
	if (frm >= 256):
	   frm = 0

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
