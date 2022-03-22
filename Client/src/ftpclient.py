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
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("Failed to create socket!")
        sys.exit()
    server_socket.bind((host, port))
    server_socket.listen()
    while True:
        conn, addr = server_socket.accept()
        print(conn, addr)
        conn.close()
    pass
