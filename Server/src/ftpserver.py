import socket
import socketserver
import threading
import pickle
import sys
from serverlog import MyLogger
import statcode
from Server.src.ops import dir_op, file_op, user_op, userdbop

HOST = socket.gethostname()
PORT = 6666
FILE_PATH_ROOT = '../workspace'
CONTENT_SIZE = 4 * 1024
BUFFER_SIZE = 5 * 1024


class MyHandle(socketserver.StreamRequestHandler):
    def handle(self):
        my_server = None
        while True:
            data = pickle.loads(self.request.recv(BUFFER_SIZE))
            # any server_op package from client used for heart beat
            if data['op_type'] == 'server_op':
                continue
            if my_server is None:
                my_server = FtpServer(self.request)
            try:
                getattr(my_server, data['op_type'])(data['op_code'], data['content'])
            except AttributeError:
                MyLogger.warning('An undefined operation({}) was attempted by address({})'.format(data['op_type'], self.request.client_address))


class FtpServer:
    __inline_users = []
    __lock = threading.Lock()
    __socket = None
    __root = FILE_PATH_ROOT

    def __init__(self, conn):
        self.conn = conn
        self.address = conn.client_address
        self.username = None

    @staticmethod
    def start_server(host, port):
        try:
            FtpServer.__socket = socketserver.TCPServer((host, port), MyHandle)
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
            except ValueError:
                MyLogger.info('User({}) logged out tried to log out'.format(user))
            finally:
                FtpServer.__lock.release()

    @staticmethod
    def get_inline_users():
        return FtpServer.__inline_users[:]

    def __log_op_warning(self, op, code):
        if self.username is None:
            MyLogger.warning('An undefined {} operation({}) was attempted by address({})'.format(op, code, self.address))
        else:
            MyLogger.warning('An undefined {} operation({}) was attempted by user({})'.format(op, code, self.username))

    def user_op(self, code, content):
        closed = False
        ret_data = {'op_type': 'server_op', 'op_code': statcode.SERVER_ERR}
        if code == statcode.USER_REG_REQ:
            status = user_op.user_reg(content['username'], content['password'])
            if status == userdbop.STATUS_OK:
                MyLogger.info('User({}) been registered'.format(content['username']))
                ret_data['op_code'] = statcode.SERVER_OK
            elif status == userdbop.STATUS_USER_EXISTED:
                ret_data['content'] = 'this username had been used'
            else:
                MyLogger.info('{} failed to register with unknown error'.format(self.address))
                ret_data['content'] = 'Unknown error'
        elif code == statcode.USER_LOGIN_REQ:
            status = user_op.user_login(content['username'], content['password'])
            if status == userdbop.STATUS_OK:
                self.username = content['username']
                FtpServer.add_inline_user(self.username)
                ret_data['op_code'] = statcode.SERVER_OK
            elif status == userdbop.STATUS_NOT_EXIST or status == userdbop.STATUS_WRONG_PASSWD:
                MyLogger.info('{} tried to login with wrong username or password'.format(self.address))
                ret_data['content'] = 'Wrong username or password'
            elif status == userdbop.STATUS_USER_CANCELED:
                MyLogger.info('{} tried to login with cancelled user({})'.format(self.address, content['username']))
                ret_data['content'] = 'User had been cancelled'
            else:
                MyLogger.info('{} failed to login with unknown error'.format(self.address))
                ret_data['content'] = 'Unknown error'
        elif code == statcode.USER_LOGOUT_REQ:
            FtpServer.del_inline_user(self.username)
            ret_data['op_code'] = statcode.SERVER_OK
            closed = True
        elif code == statcode.USER_DEL_REQ:
            status = user_op.user_del(content['username'], content['password'])
            if status == userdbop.STATUS_OK:
                if content['username'] in FtpServer.get_inline_users():
                    FtpServer.del_inline_user(content['username'])
                ret_data['op_code'] = statcode.SERVER_OK
                closed = True
            elif status == userdbop.STATUS_NOT_EXIST:
                MyLogger.info('{} tried to delete an unknown user'.format(self.address))
                ret_data['content'] = 'Unknown username'
            elif status == userdbop.STATUS_WRONG_PASSWD:
                MyLogger.info('{} tried to delete user({}) with wrong password'.format(self.address, content['username']))
                ret_data['content'] = 'Wrong username or password'
            else:
                MyLogger.info('{} failed to delete user({}) with unknown error'.format(self.address, content['username']))
                ret_data['content'] = 'Unknown error'
        else:
            self.__log_op_warning('user', code)
            return
        self.conn.send(pickle.dumps(ret_data))
        if closed:
            self.conn.close()

    def dir_op(self, code, content):
        if code == statcode.USER_REG_REQ:
            pass
        elif code == statcode.USER_LOGIN_REQ:
            pass
        elif code == statcode.USER_LOGOUT_REQ:
            pass
        elif code == statcode.USER_DEL_REQ:
            pass
        else:
            self.__log_op_warning('dir', code)

    def file_op(self, code, content):
        if code == statcode.USER_REG_REQ:
            pass
        elif code == statcode.USER_LOGIN_REQ:
            pass
        elif code == statcode.USER_LOGOUT_REQ:
            pass
        elif code == statcode.USER_DEL_REQ:
            pass
        else:
            self.__log_op_warning('file', code)


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
    pass
