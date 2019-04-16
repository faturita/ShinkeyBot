#coding: latin-1
#
# STEM - Blinking Counter

# Este programa es un ejemplo de utilizacion de python para implementar un simple
# contador de penstaneos basados en una senal de EMG/EMG/EOG.
#
# Frecuencia de sampleo Fs = 128
import csv
import numpy as np

import scipy.signal as signal

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def corrections(a,n=300):
    cumlist = []
    for source in range(1, len(a)-n,n):
        cum = 0
        for i in range(source, source+n):
            if (a[i-1] + 1==a[i]) or (a[i-1] == 254 and a[i]==0):
                pass
            else:
                cum = cum + 1
        cumlist.append(cum)

    return cumlist

results = []

print 'Este programa tiene que ejecutarse con python 2.7!'

# Esta primera linea, abre el archivo 'blinking.dat' que se grabó
# al establecerse la conexión con el servidor.
with open('sensor1.dat') as inputfile:
    for row in csv.reader(inputfile):
        rows = row[0].split(' ')
        results.append(rows[0:])

# Convert the file into numpy array of ints.
results = np.asarray(results)
results = results.astype(float)

# Strip from the signal anything you want


# La primer columna corresponde a el largo del archivo a considerar
# en relación a las muestras (1:100 serian las muestras) representante
# del tiempo.
# La segunda columna, corresponde a: eeg, attention y meditation.
#data = results[0:,0
data = results

mylist = data[0:,2]

N = 300
cumsum, moving_aves = [0], []

for i, x in enumerate(mylist, 1):
    cumsum.append(cumsum[i-1] + x)
    if i>=N:
        moving_ave = (cumsum[i] - cumsum[i-N])/N
        #can do stuff with moving_ave here
        moving_aves.append(moving_ave)


fps = moving_average(data[0:,1], n=5000)
voltages = moving_average(data[0:,2], n=300)
current = moving_average(data[0:,3],n=300)
freq = moving_average(data[0:,4], n=5000)
s = corrections(data[0:,5],n=5000)


import matplotlib.pyplot as plt
fig = plt.figure()
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

ax2.plot(freq,'r', label='Fps')
#ax1.plot(data[0:,2],'g', label='V')
ax3.plot(current,'b', label='A')
ax1.plot(voltages,'g', label='V')
#ax1.plot(data[0:,4],'y', label='A')
plt.legend(loc='upper left');
plt.show()


fig = plt.figure()
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

ax2.plot(freq,'r', label='Freq')
ax1.plot(fps,'y', label='Fps')
ax3.plot(s, 'b', label='Errors')
plt.legend(loc='upper left');
plt.show()
