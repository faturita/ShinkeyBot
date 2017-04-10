#coding: latin-1

# Read the sensor data captured by SensorimotorLogger and plot the data.



import matplotlib.pyplot as plt
f = open('sensor.2017-04-07-22-09-00.dat', 'rw')
dat = f.readline()

x = []
y = []
z = []

while len(dat) > 0:
   data = dat.split('\n')[0].split(' ')

   x.append( float(data[12]) )
   y.append( float(data[13]) )
   z.append( float(data[14]) )

   dat = f.readline()


import numpy as np

print str((np.array(x)).mean())
print str((np.array(y)).mean())
print str((np.array(z)).mean())

plt.plot(x,'r', label='X')
plt.plot(y,'g', label='Y')
plt.plot(z,'b', label='Z')

plt.show()
