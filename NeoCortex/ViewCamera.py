import numpy as np
import cv2

#import pyserial

cap = cv2.VideoCapture(0)

#window = namedWindow("TheWindow",1)
#ser = serial.Serial(port='/dev/tty.usbserial-AD01QBMW', timeout=0)

while(True):
   # Capture frame-by-frame
   ret, frame = cap.read()

   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
   cv2.imwrite('01.png', gray)

   cv2.imshow("My Image", gray)

   if cv2.waitKey(1) & 0xFF == ord('q'):
      break

#When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
