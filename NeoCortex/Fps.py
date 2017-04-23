import time

# Start time
start = time.time()

num_frames = 0

while (True):

    # End time
    end = time.time()

    # Time elapsed
    seconds = end - start
    print "Time taken : {0} seconds".format(seconds)

    num_frames = num_frames + 1

    if (seconds>1):
        break


# Calculate frames per second
fps  = num_frames / seconds;
print "Estimated frames per second : {0}".format(fps);
