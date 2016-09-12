import Proprioceptive as prop
import time
import unittest

def whoisthis(module):
    module.write('I')
    time.sleep(1)
    id = module.read(5)
    return id

class ModuleTest(unittest.TestCase):
    def testunplugged(self):
        raw_input("Unplug the boards.")

        [smnr, mtrn] = prop.serialcomm()

        self.assertEqual(smnr,None)
        self.assertEqual(mtrn,None)


    def test(self):
        [smnr, mtrn] = prop.serialcomm()
        print smnr.read(250)
        print mtrn.read(250)


        print "SMNR Serial Port:", smnr.port
        print "MTRN Serial Port:", mtrn.port

        self.assertEqual(whoisthis(smnr)[0:4],'SSMR')
        self.assertEqual(whoisthis(mtrn)[0:4],'MTRN')

        smnr.close()
        mtrn.close()

    def testtxrx(self):
        [smnr, mtrn] = prop.serialcomm()
        
        print 'Testing serial comm'
        mtrn.write('D')
        smnr.write('D')

        print "SMNR Serial Port:", smnr.port
        print "MTRN Serial Port:", mtrn.port

        print "Tilt down"
        smnr.write('T')
        time.sleep(3)
        print "Go back"
        smnr.write('G')
        time.sleep(3)
        print "Pan Left"
        smnr.write('H')
        time.sleep(3)
        print "Pan Right"
        smnr.write('F')
        time.sleep(3)
        print "Go back"
        smnr.write('G')
        

        for i in range(1,10000):
            mtrn.write('A1200')
            smnr.write('S')

            rsp = mtrn.read(250)
            rsp = smnr.read(250)
            
        print "SMNR Serial Port:", smnr.port
        print "MTRN Serial Port:", mtrn.port
        print "Done"


    def runTest(self):
        pass

test = ModuleTest()
test.testtxrx()





