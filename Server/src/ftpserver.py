import os.path
import socket
import socketserver
import pickle
import sys
import threading
import ssl
import struct
from serverlog import MyLogger
import statcode
from Server.src.ops import dir_op, file_op, user_op, userdb_op

HOST = socket.gethostname()
PORT = 6666
FILE_PATH_ROOT = r'..\workspace'
CONTENT_SIZE = 4 * 1024
BUFFER_SIZE = 5 * 1024
VALID_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_'
CERT_FILE = r'..\..\cert.pem'
KEY_FILE = r'..\..\key.pem'


def str_valid(_str):
    """
    judge if a str is valid or not
    :param _str: a string
    :return: a boolean
    """
    if len(_str) == 0:
        return False
    valid = True
    for ch in _str:
        if ch not in VALID_CHARS:
            valid = False
    return valid


class MyHandle(socketserver.StreamRequestHandler):
    def handle(self):
        my_server = None
        try:
            while True:
                b_length = self.request.recv(4)
                r_len = len(b_length)
                while r_len != 4:
                    b_length = self.request.recv(4)
                    r_len = len(b_length)
                length = struct.unpack('>I', b_length)[0]
                data = pickle.loads(self.request.recv(length))
                # any server_op package from client used for heart beat
                try:
                    if data['op_type'] == statcode.SERVER_OP:
                        continue
                except KeyError:
                    continue
                if my_server is None:
                    my_server = FtpServer(self.request, self.client_address)
                try:
                    getattr(my_server, data['op_type'])(data['op_code'], data['content'])
                except AttributeError:
                    MyLogger.warning('An undefined operation({}) was attempted by address({})'
                                     ''.format(data['op_type'],
                                               self.client_address))
        except ConnectionResetError:
            return


class MySSLTCPServer(socketserver.TCPServer):
    def __init__(self, address, handle, cert, key, ssl_version=ssl.PROTOCOL_TLSv1):
        super().__init__(address, handle)
        self.cert = cert
        self.key = key
        self.ssl_version = ssl_version

    def get_request(self):
        conn, addr = self.socket.accept()
        ssl_conn = ssl.wrap_socket(conn,
                                   server_side=True,
                                   certfile=self.cert,
                                   keyfile=self.key,
                                   ssl_version=self.ssl_version)
        return ssl_conn, addr


class MySSLThreadingTCPServer(socketserver.ThreadingMixIn, MySSLTCPServer):
    pass


class FtpServer:
    __inline_users = []
    __lock = threading.Lock()
    __socket = None
    __root = FILE_PATH_ROOT

    def __init__(self, conn, address):
        self.conn = conn
        self.address = address
        self.username = None
        self.cwd = None  # current work dir
        self.send_fd = None
        self.send_name = None
        self.recv_fd = None
        self.recv_name = None
        self.obj_recv_size = 0
        self.cur_recv_size = 0

    @staticmethod
    def start_server(host, port):
        try:
            FtpServer.__socket = MySSLThreadingTCPServer((host, port), MyHandle, CERT_FILE, KEY_FILE)
        except socket.error:
            MyLogger.critical('Failed to create ftp server')
            sys.exit()

        try:
            FtpServer.__socket.serve_forever()
        except socket.error:
            MyLogger.critical('Failed to start ftp server or other unknown error')
        finally:
            if FtpServer.__socket is not None:
                FtpServer.__socket.server_close()

    @staticmethod
    def add_inline_user(user):
        if user is not None and user not in FtpServer.__inline_users:
            try:
                FtpServer.__lock.acquire()
                FtpServer.__inline_users.append(user)
            finally:
                FtpServer.__lock.release()
                MyLogger.info('User({}) logged in'.format(user))

    @staticmethod
    def del_inline_user(user):
        if user is not None and user not in FtpServer.__inline_users:
            MyLogger.info('User({}) logged out tried to log out'.format(user))
        else:
            try:
                FtpServer.__lock.acquire()
                FtpServer.__inline_users.remove(user)
                MyLogger.info('User({}) logged out'.format(user))
            except ValueError:
                MyLogger.info('User({}) logged out tried to log out'.format(user))
            finally:
                FtpServer.__lock.release()

    @staticmethod
    def get_inline_users():
        return FtpServer.__inline_users[:]

    def __log_op_warning(self, op, code):
        if self.username is None:
            MyLogger.warning(
                'An undefined {} operation({}) was attempted by address({})'.format(op, code, self.address))
        else:
            MyLogger.warning('An undefined {} operation({}) was attempted by user({})'.format(op, code, self.username))

    def __send_frame(self, ret_data):
        frame = pickle.dumps(ret_data)
        self.conn.send(struct.pack('>I', len(frame)))
        self.conn.send(frame)

    def user_op(self, code, content):
        ret_data = {'op_type': statcode.SERVER_OP, 'op_code': statcode.SERVER_ERR}
        if code == statcode.USER_REG_REQ:
            if not str_valid(content['username']):
                return
            status = user_op.user_reg(content['username'], content['password'])
            if status == userdb_op.STATUS_OK:
                MyLogger.info('User({}) been registered'.format(content['username']))
                ret_data['op_code'] = statcode.SERVER_OK
            elif status == userdb_op.STATUS_USER_EXISTED:
                ret_data['content'] = 'this username had been used'
            else:
                MyLogger.info('{} failed to register with unknown error'.format(self.address))
                ret_data['content'] = 'Unknown error'
        elif code == statcode.USER_LOGIN_REQ:
            status = user_op.user_login(content['username'], content['password'])
            if status == userdb_op.STATUS_OK:
                self.cwd = self.username = content['username']
                FtpServer.add_inline_user(self.username)
                ret_data['op_code'] = statcode.SERVER_OK
                ret_data['content'] = 'User logged in'
            elif status == userdb_op.STATUS_NOT_EXIST or status == userdb_op.STATUS_WRONG_PASSWD:
                MyLogger.info('{} tried to login with wrong username or password'.format(self.address))
                ret_data['content'] = 'Wrong username or password'
            elif status == userdb_op.STATUS_USER_CANCELED:
                ret_data['op_code'] = statcode.SERVER_REJ
                MyLogger.info('{} tried to login with cancelled user({})'.format(self.address, content['username']))
                ret_data['content'] = 'User had been cancelled'
            else:
                MyLogger.info('{} failed to login with unknown error'.format(self.address))
                ret_data['content'] = 'Unknown error'
        elif code == statcode.USER_LOGOUT_REQ:
            FtpServer.del_inline_user(self.username)
            self.username = None
            self.cwd = None
            ret_data['op_code'] = statcode.SERVER_OK
        elif code == statcode.USER_DEL_REQ:
            status = user_op.user_del(content['username'], content['password'])
            if status == userdb_op.STATUS_OK:
                if content['username'] in FtpServer.get_inline_users():
                    FtpServer.del_inline_user(content['username'])
                self.username = None
                self.cwd = None
                ret_data['op_code'] = statcode.SERVER_OK
                ret_data['content'] = 'User cancel ok'
            elif status == userdb_op.STATUS_NOT_EXIST:
                MyLogger.info('{} tried to delete an unknown user'.format(self.address))
                ret_data['content'] = 'Unknown username'
            elif status == userdb_op.STATUS_WRONG_PASSWD:
                MyLogger.info(
                    '{} tried to delete user({}) with wrong password'.format(self.address, content['username']))
                ret_data['content'] = 'Wrong username or password'
            else:
                MyLogger.info(
                    '{} failed to delete user({}) with unknown error'.format(self.address, content['username']))
                ret_data['content'] = 'Unknown error'
        else:
            self.__log_op_warning('user', code)
            return
        self.__send_frame(ret_data)

    def __dir_log(self, op, path, code):
        MyLogger.info('User({}) {} dir({})-status({})'.format(self.username, op, path, code))

    def dir_op(self, code, content):
        ret_data = {'op_type': statcode.SERVER_OP, 'op_code': statcode.SERVER_ERR}
        if self.username is None:
            return
        elif code == statcode.DIR_REQ:
            if content == '..\\':
                if self.cwd == self.username:
                    ret_data['op_code'] = statcode.SERVER_REJ
                    ret_data['content'] = 'No right to access'
                    self.__send_frame(ret_data)
                    return
                self.cwd = os.path.join(*self.cwd.split('\\')[:-1])
            elif content != '':
                self.cwd = os.path.join(self.cwd, content)
            ret_data['op_code'], ret_data['content'] = dir_op.dir_get(self.username, self.cwd)
            self.__dir_log('get', self.cwd, ret_data['op_code'])
        elif code == statcode.DIR_CREATE_REQ:
            ret_data['op_code'] = dir_op.dir_create(self.username, self.cwd, content)
            self.__dir_log('create', os.path.join(self.cwd, content), ret_data['op_code'])
        elif code == statcode.DIR_DEL_REQ:
            ret_data['op_code'] = dir_op.dir_del(self.username, self.cwd, content)
            self.__dir_log('delete', os.path.join(self.cwd, content), ret_data['op_code'])
        else:
            self.__log_op_warning('dir', code)
        self.__send_frame(ret_data)

    def file_op(self, code, content):
        ret_data = {'op_type': statcode.SERVER_OP, 'op_code': statcode.SERVER_ERR}
        is_send = False
        if self.username is None:
            return
        if code == statcode.FILE_DOWNLOAD_REQ:
            ret_data['op_code'], self.send_fd = file_op.file_download(self.username, self.cwd, content)
            self.send_name = content
            is_send = True
        elif code == statcode.FILE_UPLOAD_REQ:
            ret_data['op_code'], self.recv_fd = file_op.file_upload(self.username, self.cwd, content)
            self.recv_name = content
        elif code == statcode.FILE_DEL_REQ:
            ret_data['op_code'] = file_op.file_del(self.username, self.cwd, content)
            MyLogger.info('User({}) delete file({})-status({})'.format(self.username,
                                                                       os.path.join(self.cwd, content),
                                                                       ret_data['op_code']))
        elif code == statcode.FILE_META and self.recv_fd is not None:
            self.obj_recv_size = content['size']
            return
        elif code == statcode.FILE_CONT and self.recv_fd is not None:
            self.recv_file(content)
            return
        else:
            self.__log_op_warning('file', code)
        self.__send_frame(ret_data)
        if is_send:
            self.send_file()

    def send_file(self):
        obj_size = os.path.getsize(os.path.join(FILE_PATH_ROOT, self.cwd, self.send_name))
        frame = {
            'op_type': statcode.FILE_OP,
            'op_code': statcode.FILE_META,
            'content': {'name': self.send_name, 'size': obj_size}
        }
        self.__send_frame(frame)
        frame['op_code'] = statcode.FILE_CONT
        while obj_size > 0:
            frame['content'] = self.send_fd.read(CONTENT_SIZE)
            self.__send_frame(frame)
            obj_size -= CONTENT_SIZE
        self.send_fd.close()
        self.send_fd = None
        MyLogger.info('User({}) download file({})-status({})'.format(self.username,
                                                                     os.path.join(self.cwd, self.send_name),
                                                                     statcode.SERVER_OK))

    def recv_file(self, content):
        self.cur_recv_size += len(content)
        self.recv_fd.write(content)
        if self.cur_recv_size >= self.obj_recv_size:
            self.recv_fd.close()
            self.recv_fd = None
            self.obj_recv_size = self.cur_recv_size = 0
            MyLogger.info('User({}) upload file({})-status({})'.format(self.username,
                                                                       os.path.join(self.cwd, self.recv_name),
                                                                       statcode.SERVER_OK))


if __name__ == '__main__':
    host = socket.gethostname()
    port = 6666
    file_path = r'..\workspace\test\1.txt'
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
        tmp = pickle.dumps(file_meta)
        conn.send(struct.pack('>I', len(tmp)))
        conn.send(tmp)
        with open(file_path, 'rb') as f:
            data = f.read(4 * 1024)
        file_content = {
            'type': 'content',
            'num': 0,
            'content': data
        }
        tmp = pickle.dumps(file_content)
        conn.send(struct.pack('>I', len(tmp)))
        conn.send(tmp)
        conn.close()
    pass
