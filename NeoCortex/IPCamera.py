#coding: latin-1
import cv2
import time
import datetime
import numpy as np
import argparse

import sys

import Configuration as conf

import ConfigMe
import io

import os

savevideo = True

if (len(sys.argv)<2):
	# Load the configuration file
	ip = ConfigMe.readconfig("config.ini")
	port = conf.videoport

elif sys.argv[1] == '-f':
	print "Forcing IP Address"
	ip = '192.168.0.110'
	port = 10000
else:
	ip = sys.argv[1]
	print "Using IP:"+ip
	port = 10000


#cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture('/Users/rramele/Documents/AppleStore.Subiendo.I.mov')
#cap = cv2.VideoCapture('tcp://192.168.1.1:5555')
#cap = cv2.VideoCapture('tcp://192.168.0.3/cgi-bin/fwstream.cgi?FwModId=0&PortId=1&PauseTime=0&FwCgiVer=0x0001')
#cap = cv2.VideoCapture('rtsp://192.168.0.3/cam0_0')
#cap = cv2.VideoCapture('tcp://192.168.0.110:10000')
#cap = cv2.VideoCapture('tcp://10.17.48.177:10000')
cap = cv2.VideoCapture('tcp://'+str(ip)+':'+str(port))

if (savevideo):
	w = cap.get(cv2.CAP_PROP_FRAME_WIDTH);
	h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT);
	fourcc = cv2.VideoWriter_fourcc(*"MJPG")
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
	out = cv2.VideoWriter('../data/output.'+st+'.avi',fourcc, 24.0, (int(w),int(h)))

print ("Connecting..")

def click_and_crop(event, x, y, flags, param):

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_RBUTTONDOWN:
		print (x, y)

cv2.namedWindow("ShinkeyBot Eye")
cv2.setMouseCallback("ShinkeyBot Eye", click_and_crop)


def hough(frame):
    edges = cv2.Canny(frame,50,150,apertureSize = 3)
    minLineLength = 100
    maxLineGap = 10
    lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(frame,(x1,y1),(x2,y2),(0,255,0),2)
	return frame



for i in range(1,80000):
	# Capture frame-by-frame
	ret, frame = cap.read()

	#frame = cv2.flip(frame,0)
	#frame = cv2.flip(frame,1)

	#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#cv2.imwrite('01.png', gray)

	#Using AKAZE descriptors.
	#detector = cv2.AKAZE_create()
	#(kps, descs) = detector.detectAndCompute(gray, None)
	#print("keypoints: {}, descriptors: {}".format(len(kps), descs.shape))

	# draw the keypoints and show the output image
	#cv2.drawKeypoints(frame, kps, frame, (0, 255, 0))

	#edges = cv2.Canny(frame,100,200)
	#edges = cv2.Canny(frame,50,150,apertureSize = 3)

	# Convert BGR to HSV
	# Convert BGR to HSV
	##hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	# define range of blue color in HSV
	##lower_blue = np.array([160,50,50])
	##upper_blue = np.array([185,255,255])


	# Threshold the HSV image to get only blue colors
	##mask = cv2.inRange(hsv, lower_blue, upper_blue)
	# Bitwise-AND mask and original image
	##res = cv2.bitwise_and(frame,frame, mask= mask)
	##res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
	##hough(res)

	#print frame[474,37]

	cv2.imshow("ShinkeyBot Eye", frame)

	if (savevideo):
		out.write(frame)

	if cv2.waitKey(1) & 0xFF == ord('q'):
	    break

print ('Done.')

#When everything done, release the capture
cap.release()
time.sleep(5)

out.release()

cv2.destroyAllWindows()
