import os
from serverlog import MyLogger
import sqlite3
import sys
from Server.src.ops import mydb, user_op
import ftpserver

LOG_PATH = r'..\log'
ROOT_PATH = r'..\workspace'


def init_db():
    conn = mydb.MyDBConn()
    try:
        conn.cursor.execute(mydb.CREATE_TABLE_SQL)
    except sqlite3.Error:
        MyLogger.critical('Failed to create table')
        sys.exit()
    finally:
        conn.release()


def init_dir():
    try:
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)
        if not os.path.exists(ROOT_PATH):
            os.mkdir(ROOT_PATH)
    except OSError:
        MyLogger.critical('Failed to create work path')
        sys.exit()


def init():
    init_db()
    init_dir()


def release_user():
    failed = user_op.user_release()
    if len(failed) != 0:
        MyLogger.error('User released: {} failed'.format(failed))


if __name__ == '__main__':
    init()
    ftpserver.FtpServer.start_server(ftpserver.HOST, ftpserver.PORT)
    pass
