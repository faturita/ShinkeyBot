import sys
import os
 
original = sys.stdout
out = open('./console.log', 'w')
sys.stdout = out
sys.stderr = out
print('Init')
#sys.stdout = original

# import socket

# def internet(host="8.8.8.8", port=53, timeout=3):
#   """
#   Host: 8.8.8.8 (google-public-dns-a.google.com)
#   OpenPort: 53/tcp
#   Service: domain (DNS/TCP)
#   """
#   try:
#     socket.setdefaulttimeout(timeout)
#     socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
#     return True
#   except socket.error as ex:
#     print(ex)
#     return False

# if (not internet()):
#     print("Network unavailable.")
#     quit(1)


if (os.access("running.wt", os.W_OK)):
    os.remove("running.wt")
    

import Brainstem
