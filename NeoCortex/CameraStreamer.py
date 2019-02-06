# Camera Streamer
#
# Picks data from the VideoCapture device and transmit frame by frame directly
# through TCP/IP
#
# Marks each frame to understand how the data should be read on the other side
#
# It's extremly inefficient
#
# 

import numpy as np
import cv2

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#server_address = ('192.168.0.106', 10000)
server_address = ('127.0.0.1', 10000)
server_address = ('10.17.13.84', 10000)

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

frm = 0

sock.connect(server_address)

while(True):
   # Capture frame-by-frame
   ret, frame = cap.read()
   #frame = cv2.imread("screenshot1.png")

   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

   frm = frm + 1
   if (frm >= 256):
       frm = 0

   data = np.zeros((640), dtype=np.uint8)
   data[0] = data[1] = data[2] = data[3] = data[5] = 32
   sent = sock.sendto(data, server_address)

   # for i in range(1,480):
   #     data = gray[i,:]
   #     sent = sock.sendto(data, server_address)


   data = gray.reshape(640*480,1)
   sent = sock.sendto(data, server_address)

   #cv2.imshow("My Image", gray)

   if cv2.waitKey(1) & 0xFF == ord('q'):
      break

#When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
