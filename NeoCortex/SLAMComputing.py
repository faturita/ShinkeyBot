from TelemetryDictionary import telemetrydirs

import datetime
import time

class SLAMComputer:
    def __init__(self):
        x=0
        y=0
        heading=0
        distance=0
        self.keypoint = (x,y,heading,distance)

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        self.f = open('./data/sensor.'+'slam'+'.'+st+'.dat', 'w')

        tick = 0

    def compute(self,state, sensors):

        action = ''  # Do nothing by default

        if (state == 0):
            action = 'U,000'
            state = 1
            self.tick=0
        elif (state == 1):
            action = 'UA000'
            state = 2
        elif (state == 2):
            self.tick = self.tick + 1
            if (self.tick >= 40):
                action = 'UO000'
                state = 3
                self.tick = 0
        elif (state == 3):
            self.tick = self.tick + 1
            if (self.tick >= 40):
                state = 0
                self.tick = 0       

        self.keypoint = (0,0,sensors[telemetrydirs['geoHeading']], sensors[telemetrydirs['scanned']])

        self.f.write( str(self.keypoint) + '\n')
        self.f.flush()


        return [state, action]