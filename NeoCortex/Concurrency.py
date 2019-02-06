# Test concurrency issues

import Queue
import thread

class Sensorimotor:
    def __init__(self, queue):
        self.queue = queue

    def loop(self):
        i = 0
        while (True):
            self.queue.put(i)
            i = i + 1

            if (i>80):
                i=0

q = Queue.Queue()
sur = Sensorimotor(q)

try:
    thread.start_new_thread( sur.loop, () )
    pass
except:
    pass

while (True):
    i = q.get()
    print i
