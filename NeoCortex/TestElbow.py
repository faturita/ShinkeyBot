import Proprioceptive as prop
[smnr, mtrn] = prop.serialcomm()
import time
time.sleep(1)
mtrn.read(1000)
mtrn.write('A6080')
time.sleep(2)
mtrn.write('AA120')
time.sleep(2)
mtrn.read(11111)
mtrn.close()
smnr.close()
