from Server.src.ops.mydb import MyDBConn
from werkzeug.security import generate_password_hash, check_password_hash

HASH_METHOD = 'pbkdf2:sha256'
SALT_LENGTH = 8

STATUS_OK = 0
STATUS_FAILED = 1
STATUS_NOT_EXIST = 11
STATUS_WRONG_PASSWD = 12
STATUS_USER_EXISTED = 13
STATUS_USER_CANCELED = 14


def exists(username):
    """
    select table to check if exists user called username or not
    :param username: username for log in
    :return: result tuple and connection to database
    """
    conn = MyDBConn()
    user = conn.select("SELECT * FROM USERS WHERE USERNAME = ?", (username, ))
    return user, conn


def add_user(username, password):
    """
    try to add user to database, and need hash user's password for encrypt
    :param username: username for log in
    :param password: password for log in
    :return: op status
    """
    user, conn = exists(username)
    try:
        if len(user) != 0:
            return STATUS_USER_EXISTED
        hash_passwd = generate_password_hash(password, HASH_METHOD, SALT_LENGTH)[len(HASH_METHOD) + 1:]
        if conn.update("INSERT INTO USERS (USERNAME, PASSWORD) VALUES (?, ?)", (username, hash_passwd)):
            return STATUS_OK
        return STATUS_FAILED
    finally:
        conn.release()


def check_user_passwd(username, password):
    """
    check user's password is correct or not
    :param username: username for log in
    :param password: password for log in
    :return: op status
    """
    user, conn = exists(username)
    try:
        if len(user) == 0:
            return STATUS_NOT_EXIST
        if user[0][2]:
            return STATUS_USER_CANCELED
        hash_passwd = HASH_METHOD + ':' + user[0][1]
        if check_password_hash(hash_passwd, password):
            return STATUS_OK
        return STATUS_WRONG_PASSWD
    finally:
        conn.release()


def cancel_user(username):
    """
    cancel user's account
    :param username: username for log in
    :return: op status
    """
    user, conn = exists(username)
    try:
        if len(user) == 0:
            return STATUS_NOT_EXIST
        if conn.update("UPDATE USERS SET CANCELLED = ? WHERE USERNAME = ?", (True, username)):
            return STATUS_OK
        return STATUS_FAILED
    finally:
        conn.release()


def update_user_permission(username, privilege):
    """
    update user's permission for download speed with privilege level
    :param username: username for log in
    :param privilege: the privilege want to set
    :return: op status
    """
    user, conn = exists(username)
    try:
        if len(user) == 0 or user[0][2]:
            return STATUS_NOT_EXIST
        if conn.update("UPDATE USERS SET PERMISSION = ? WHERE USERNAME = ?", (privilege, username)):
            return STATUS_OK
        return STATUS_FAILED
    finally:
        conn.release()


def release_cancelled_user():
    """
    release cancelled users, delete cancelled users from database
    :return: tuple of cancelled users' username
    """
    conn = MyDBConn()
    try:
        users = conn.select("SELECT USERNAME FROM USERS WHERE CANCELLED = ?", (True, ))
        conn.update("DELETE FROM USERS WHERE CANCELLED = ?", (True, ))
        return tuple(item[0] for item in users)
    finally:
        conn.release()


if __name__ == '__main__':
    '''
    passwd = generate_password_hash('password', method='pbkdf2:sha256', salt_length=8)
    print(passwd[len(HASH_METHOD) + 1:])
    print(passwd[:14] + passwd[20:])
    result = check_password_hash(passwd, 'password')
    print(result)
    '''
    print(add_user('test', '123456'))
    print(add_user('test2', '123456'))
    print(add_user('test3', '123456'))
    conn = MyDBConn()
    print(conn.select("SELECT * FROM USERS WHERE USERNAME = ?", ('test', )))
    print(update_user_permission('test', 10))
    print(conn.select("SELECT * FROM USERS WHERE USERNAME = ?", ('test', )))
    # print(check_user_passwd('test', '123456'))
    # print(check_user_passwd('test', '12346'))
    print(cancel_user('test'))
    print(cancel_user('test2'))
    print(cancel_user('test3'))
    print(conn.select("SELECT * FROM USERS WHERE USERNAME = ?", ('test', )))
    # print(check_user_passwd('test', '123456'))
    # print(check_user_passwd('test', '12346'))
    # conn.update("DELETE FROM USERS WHERE USERNAME = ?", ('test',))
    print(release_cancelled_user())
    print(conn.select("SELECT * FROM USERS WHERE USERNAME = ?", ('test',)))
    conn.release()



