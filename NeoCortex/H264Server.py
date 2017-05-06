import socket
import time
import picamera
import thread

print "Openning single-client H264 streaming server:"+str(8000)
with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 10
    camera.color_effects = (128,128)

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)

    # Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('wb')
    try:
        camera.start_recording(connection, format='h264')
        camera.wait_recording(100000)
        camera.stop_recording()
    finally:
        camera.close()
        connection.close()
        server_socket.close()
        print 'Connection closed.  Camera released.'
