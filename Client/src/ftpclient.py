import socket
import pickle
import sys
import time
import os


class FtpClient:
    def __init__(self):
        pass


if __name__ == '__main__':
    host = socket.gethostname()
    port = 6666
    work_dir_root = '../workspace'
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("Failed to create socket!")
        sys.exit()
    client_socket.connect((host, port))
    file_meta = client_socket.recv(1024)
    file_meta = pickle.loads(file_meta)
    print(file_meta)
    file_content = pickle.loads(client_socket.recv(5 * 1024))
    with open(os.path.join(work_dir_root, file_meta['name']), 'wb') as f:
        f.write(file_content['content'])
    client_socket.close()
    pass
