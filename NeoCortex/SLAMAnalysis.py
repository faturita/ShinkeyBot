import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np
import csv

results = []
x = []
y = []

with open('data/slam2.dat') as inputfile:
    val = inputfile.readline()
    while len(val)>0:
        rows = val[1:-2]
        rows = rows.split(',')
        results.append([float(rows[2]),float(rows[3])])
        x.append(float(rows[2]))
        y.append(float(rows[3]))
        val = inputfile.readline()

print ('Longitud del archivo:'+str(len(results)))

print( results[1000:1100] )

# Map returns a generator, that should be casted into a list for the plot
x = list(map(lambda p: p * np.pi/180.0, x))


fig = plt.figure(figsize=(5, 5))


#x = [0,np.pi/2,np.pi,3*np.pi/2]
#y = [10,10,10,10]


plt.polar(x,y,'x')

plt.show()