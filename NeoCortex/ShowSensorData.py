import matplotlib.pyplot as plt
f = open('sensor.dat', 'rw')
dat = f.readline()

x = []
y = []
z = []

while len(dat) > 0:
   data = dat.split('\n')[0].split(' ')

   x.append( float(data[0]) )
   y.append( float(data[1]) )
   z.append( float(data[2]) )

   dat = f.readline()


import numpy as np

print str((np.array(x)).mean())
print str((np.array(y)).mean())
print str((np.array(z)).mean())

plt.plot(x)
plt.plot(y)
plt.plot(z)

plt.show()
