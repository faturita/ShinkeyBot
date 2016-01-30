import numpy as np
import cv2

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.0.106', 10000)


cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

frm = 0

sock.connect(server_address)

while(True):
   # Capture frame-by-frame
   ret, frame = cap.read()

   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

   frm = frm + 1
   if (frm >= 256):
       frm = 0

   data = np.zeros((640), dtype=np.uint8)
   sent = sock.sendto(data, server_address)

   for i in range(1,480):
       data = gray[i,:]
       sent = sock.sendto(data, server_address)

   #cv2.imshow("My Image", gray)

   if cv2.waitKey(1) & 0xFF == ord('q'):
      break

#When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
