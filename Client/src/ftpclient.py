import socket
import struct
import pickle
import sys
import time
import os

if __name__ == '__main__':
    host = socket.gethostname()
    port = 6666
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("Failed to create socket!")
        sys.exit()
    client_socket.connect((host, port))
    client_socket.close()
    pass
