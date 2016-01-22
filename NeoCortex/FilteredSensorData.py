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


from scipy.signal import butter, lfilter, freqz


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

plt.subplot(2,1,1)
#plt.plot(x)
plt.plot(y)
#plt.plot(z)


# Filter requirements.
order = 6
fs = 30.0       # sample rate, Hz
cutoff = 3.667  # desired cutoff frequency of the filter, Hz

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

# Plot the frequency response.
w, h = freqz(b, a, worN=8000)
#plt.subplot(2, 1, 1)
#plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')


# Filter the data, and plot both the original and filtered signals.
y = butter_lowpass_filter(y, cutoff, fs, order)
plt.subplot(2,1,2)
plt.plot(y)
plt.show()
