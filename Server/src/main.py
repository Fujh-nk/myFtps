from serverlog import MyLogger
import sqlite3
import sys

from Server.src.ops import mydb


def init():
    conn = mydb.MyDBConn()
    try:
        conn.cursor.execute(mydb.CREATE_TABLE_SQL)
    except sqlite3.Error:
        MyLogger.critical('Failed to create table')
        sys.exit()
    finally:
        conn.release()


if __name__ == '__main__':

    pass
