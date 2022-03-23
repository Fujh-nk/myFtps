import logging
import sqlite3
import sys

import mydb
import userdbop


def init():
    conn = mydb.MyDBConn()
    try:
        conn.cursor.execute(mydb.CREATE_TABLE_SQL)
    except sqlite3.Error:
        logging.critical('Failed to create table!')
        sys.exit()
    finally:
        conn.release()


if __name__ == '__main__':

    pass
