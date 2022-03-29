import sqlite3
from dbutils.pooled_db import PooledDB

config = {
    'database': r'..\..\MyFtps.db',
    'maxconnections': 0,
    'mincached': 5,
    'maxcached': 0,
    'maxusage': None,
    'blocking': True
}

CREATE_TABLE_SQL = '''
            CREATE TABLE IF NOT EXISTS USERS (
            USERNAME VARCHAR (20) PRIMARY KEY,
            PASSWORD VARCHAR (200) NOT NULL,
            CANCELLED BOOLEAN DEFAULT FALSE,
            PERMISSION INTEGER DEFAULT 0)
            '''


class MyDBConn:
    __dbpool = None

    def __init__(self):
        self.conn = MyDBConn.get_connect()
        self.cursor = self.conn.cursor()

    @staticmethod
    def get_connect():
        """
        get connection from database pool
        :return: a connection to db
        """
        if MyDBConn.__dbpool is None:
            MyDBConn.__dbpool = PooledDB(sqlite3, **config)
        return MyDBConn.__dbpool.connection()

    def update(self, sql, params):
        """
        insert, update or delete info from database
        :param sql: the sql used for update
        :param params: the params used for update
        :return: a bool of update operator is executed or not
        """
        flag = False
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            flag = True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            # add error log
        return flag

    def select(self, sql, params):
        """
        select from db with sql and params
        :param sql: the sql used for select
        :param params: the params for select
        :return: result tuple
        """
        result = []
        try:
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
        except sqlite3.OperationalError:
            # add error log
            pass
        return tuple(result)

    def release(self):
        """
        release database connection and cursor
        :return: None
        """
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    conn = MyDBConn()
    conn.update("INSERT INTO USERS (USERNAME, PASSWORD) VALUES (?, ?)", ('test', '123456'))
    print(conn.select("SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD = ?", ('test', '123456')))
    conn.update("DELETE FROM USERS WHERE USERNAME = ?", ('test', ))
    print(conn.select("SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD = ?", ('test', '123456')))
    conn.release()
    pass
