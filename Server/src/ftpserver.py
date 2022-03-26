import socket
import socketserver
import pickle
import sys
import os

HOST = socket.gethostname()
PORT = 6666
FILE_PATH_ROOT = '../workspace'


class MyHandle(socketserver.StreamRequestHandler):
    def handle(self):
        pass

    def user_reg(self):
        pass

    def user_login(self):
        pass

    def user_logout(self):
        pass

    def user_del(self):
        pass


class FtpServer:
    def __init__(self, root):
        self.__inline_users = []
        self.__root = root
        self.__socket = None

    def start_server(self, host, port):
        self.__socket = socketserver.TCPServer((host, port), MyHandle)
        try:
            self.__socket.serve_forever()
        finally:
            if self.__socket:
                self.__socket.server_close()

    def add_inline_user(self, user):
        if user not in self.__inline_users:
            self.__inline_users.append(user)

    def del_inline_user(self, user):
        try:
            self.__inline_users.remove(user)
        except ValueError:
            pass


if __name__ == '__main__':
    '''
    host = socket.gethostname()
    port = 6666
    file_path = '../workspace/text.txt'
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("Failed to create socket!")
        sys.exit()
    server_socket.bind((host, port))
    server_socket.listen()
    while True:
        conn, addr = server_socket.accept()
        file_meta = {
            'name': 'text.txt',
            'size': os.path.getsize(file_path)
        }

        conn.send(pickle.dumps(file_meta))
        with open(file_path, 'rb') as f:
            data = f.read(4 * 1024)
        file_content = {
            'type': 'content',
            'num': 0,
            'content': data
        }
        conn.send(pickle.dumps(file_content))
        conn.close()
    '''
    l = [1, 2, 4]
    l.remove(3)
    pass
