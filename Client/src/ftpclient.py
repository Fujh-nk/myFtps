import socket
import pickle
import sys
import threading
import os
import ssl
import struct
import statcode
from time import sleep

CONTENT_SIZE = 4 * 1024
BUFFER_SIZE = 5 * 1024
WORK_DIR_ROOT = r'..\workspace'


class FtpClient:
    def __init__(self, host, port, cert, key, ssl_version):
        try:
            self.__ssl_socket = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                                server_side=False,
                                                certfile=cert,
                                                keyfile=key,
                                                ssl_version=ssl_version)
        except socket.error:
            print("Failed to create socket!")
            sys.exit()
        self.__ssl_socket.connect((host, port))
        self.host = host
        self.port = port
        self.username = None
        self.is_beating = False

    def __recv_content(self):
        b_length = self.__ssl_socket.recv(4)
        r_len = len(b_length)
        while r_len != 4:
            b_length = self.__ssl_socket.recv(4)
            r_len = len(b_length)
        length = struct.unpack('>I', b_length)[0]
        return pickle.loads(self.__ssl_socket.recv(length))

    def __send_frame(self, frame):
        tmp = pickle.dumps(frame)
        self.__ssl_socket.send(struct.pack('>I', len(tmp)))
        self.__ssl_socket.send(tmp)

    def __heart_beat(self):
        self.is_beating = True
        while self.username is not None:
            sleep(30)
            self.__send_frame({'op_code': statcode.SERVER_OP})
        self.is_beating = False

    def __send_req_and_recv_resp(self, frame):
        self.__send_frame(frame)
        return self.__recv_content()

    def login(self, user, passwd):
        if self.username is not None:
            return False, 'User had logged in'
        frame = {'op_type': statcode.USER_OP,
                 'op_code': statcode.USER_LOGIN_REQ,
                 'content': {'username': user, 'password': passwd}}
        resp = self.__send_req_and_recv_resp(frame)
        if resp['op_type'] == statcode.SERVER_OP and resp['op_code'] == statcode.SERVER_OK:
            self.username = user
            if not self.is_beating:
                threading.Thread(target=self.__heart_beat).start()
            return True, None
        return False, resp['content']

    def logout(self):
        if self.username is not None:
            frame = {'op_type': statcode.USER_OP,
                     'op_code': statcode.USER_LOGOUT_REQ,
                     'content': ''}
            self.__send_req_and_recv_resp(frame)
            self.username = None
            return True, None
        return False, 'User not log in'

    def reg_or_cancel(self, user, passwd, op=True):
        frame = {'op_type': statcode.USER_OP,
                 'op_code': statcode.USER_DEL_REQ,
                 'content': {'username': user, 'password': passwd}}
        if op:
            frame['op_code'] = statcode.USER_REG_REQ
        resp = self.__send_req_and_recv_resp(frame)
        self.username = None
        if resp['op_type'] == statcode.SERVER_OP and resp['op_code'] == statcode.SERVER_OK:
            return True, None
        return False, resp['content']

    def get_dir(self, obj):
        frame = {'op_type': statcode.DIR_OP,
                 'op_code': statcode.DIR_REQ,
                 'content': obj}
        resp = self.__send_req_and_recv_resp(frame)
        if resp['op_type'] == statcode.SERVER_OP:
            if resp['op_code'] == statcode.SERVER_OK:
                return True, resp['content']
            elif resp['op_code'] == statcode.SERVER_REJ:
                return False, 'No right to access'
        return False, 'Unknown Error'

    def create_dir(self, obj):
        frame = {'op_type': statcode.DIR_OP,
                 'op_code': statcode.DIR_CREATE_REQ,
                 'content': obj}
        resp = self.__send_req_and_recv_resp(frame)
        if resp['op_type'] == statcode.SERVER_OP:
            if resp['op_code'] == statcode.SERVER_OK:
                return True, None
            elif resp['op_code'] == statcode.SERVER_REJ:
                return False, 'No right to access'
        return False, 'Unknown Error'

    def download(self, obj):
        frame = {'op_type': statcode.FILE_OP,
                 'op_code': statcode.FILE_DOWNLOAD_REQ,
                 'content': obj}
        resp = self.__send_req_and_recv_resp(frame)
        if resp['op_type'] == statcode.SERVER_OP:
            if resp['op_code'] == statcode.SERVER_REJ:
                return False, 'No right to access'
            elif resp['op_code'] == statcode.SERVER_ERR:
                return False, 'Unknown Error'
        # start to recv file from server
        try:
            with open(os.path.join(WORK_DIR_ROOT, obj), 'wb') as f:
                frame = self.__recv_content()
                if frame['op_type'] == statcode.FILE_OP and frame['op_code'] == statcode.FILE_META:
                    obj_size = frame['content']['size']
                    while obj_size > 0:
                        frame = self.__recv_content()
                        if frame['op_type'] == statcode.FILE_OP and frame['op_code'] == statcode.FILE_CONT:
                            f.write(frame['content'])
                            obj_size -= len(frame['content'])
                    if obj_size == 0:
                        return True, None
                    return False, 'File recv error'
                else:
                    return False, 'Server Error'
        except OSError:
            return False, 'Failed to open file'

    def upload(self, obj):
        frame = {'op_type': statcode.FILE_OP,
                 'op_code': statcode.FILE_UPLOAD_REQ,
                 'content': os.path.basename(obj)}
        resp = self.__send_req_and_recv_resp(frame)
        if resp['op_type'] == statcode.SERVER_OP:
            if resp['op_code'] == statcode.SERVER_REJ:
                return False, 'No right to access'
            elif resp['op_code'] == statcode.SERVER_ERR:
                return False, 'Unknown Error'
        # start to send file to server
        try:
            frame = {'op_type': statcode.FILE_OP,
                     'op_code': statcode.FILE_META,
                     'content': {'name': os.path.basename(obj), 'size': os.path.getsize(obj)}}
            self.__send_frame(frame)
            frame['op_code'] = statcode.FILE_CONT
            with open(obj, 'rb') as f:
                frame['content'] = f.read(CONTENT_SIZE)
                self.__send_frame(frame)
        except OSError:
            return False, 'Failed to open file'
        return True, None

    def delete(self, obj, obj_type='FILE'):
        frame = {'op_type': statcode.FILE_OP,
                 'op_code': statcode.FILE_DEL_REQ,
                 'content': obj}
        if obj_type == 'DIR':
            frame['op_type'] = statcode.DIR_OP
            frame['op_code'] = statcode.DIR_DEL_REQ
        resp = self.__send_req_and_recv_resp(frame)
        if resp['op_type'] == statcode.SERVER_OP:
            if resp['op_code'] == statcode.SERVER_OK:
                return True, None
            elif resp['op_code'] == statcode.SERVER_REJ:
                return False, 'No right to access'
        return False, 'Unknown Error'


if __name__ == '__main__':
    """
    host = socket.gethostname()
    port = 6666
    work_dir_root = '../workspace'
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print("Failed to create socket!")
        sys.exit()
    client_socket.connect((host, port))
    a = ''
    while len(a) != 4:
        a = client_socket.recv(4)
    print(a, len(a))
    length = struct.unpack('>I', a)[0]
    print(length)
    file_meta = client_socket.recv(length)
    file_meta = pickle.loads(file_meta)
    print(file_meta)
    length = struct.unpack('>I', client_socket.recv(4))[0]
    print(length)
    file_content = pickle.loads(client_socket.recv(length))
    with open(os.path.join(work_dir_root, file_meta['name']), 'wb') as f:
        f.write(file_content['content'])
    client_socket.close()
    """
    pass
