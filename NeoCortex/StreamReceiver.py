import sys, select
import numpy as np
import cv2
import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('0.0.0.0', 10000)
print >> sys.stderr, 'starting up on %s port %s', server_address

sock.bind(server_address)

#cap = cv2.VideoCapture(0)

sock.listen(1)

# Wait for a connection
print >>sys.stderr, 'waiting for a connection'

connection, client_address = sock.accept()

image = np.zeros((480,640), dtype=np.uint8)

frm = 0
while(True):
   # Capture frame-by-frame
   #ret, frame = cap.read()

   while(True):
       data, address = connection.recvfrom(640)
       d = struct.unpack("640B", data)
       if (np.count_nonzero(d) == 640):
           break

   for i in range(1,480):
       data, address = connection.recvfrom(640)
       d = struct.unpack("640B", data)

       image[i,:] = d
           #image[i,j] = struct.unpack("B", data[j])[0]

   #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
   gray = image
   #cv2.imwrite('01.png', gray)

   cv2.imshow("My Image", gray)

   if cv2.waitKey(1) & 0xFF == ord('q'):
      break

#When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
