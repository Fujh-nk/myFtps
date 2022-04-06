import os.path

from Server.src.ops import userdb_op
from Server.src.ops import acl_op


def user_reg(user, passwd):
    """
    try to register user in database and local host
    :param user: username
    :param passwd: password used for log in
    :return: this operation status
    """
    status = userdb_op.add_user(user, passwd)
    if status == userdb_op.STATUS_OK:
        try:
            user_path = os.path.join(acl_op.WORK_REL_PATH, user)
            if not os.path.exists(user_path):
                os.mkdir(user_path)
            acl_op.acl_user(user, acl_op.ACL_OP_ADD)
        except acl_op.AclError as e:
            status = userdb_op.STATUS_FAILED
        except OSError as e:
            status = userdb_op.STATUS_FAILED
    return status


def user_login(user, passwd):
    """
    try to log in with user and passwd
    :param user: username
    :param passwd: password used for log in
    :return: this operation status
    """
    return userdb_op.check_user_passwd(user, passwd)


def user_del(user, passwd):
    """
    try to del user with user and passwd
    :param user: username
    :param passwd: password used for log in
    :return: this operation status
    """
    status = userdb_op.check_user_passwd(user, passwd)
    if status == userdb_op.STATUS_OK:
        status = userdb_op.cancel_user(user)
    return status


def user_release():
    """
    release cancelled username at database and local host
    :return: the users that failed to del at local host
    """
    failed = []
    for user in userdb_op.release_cancelled_user():
        try:
            acl_op.acl_user(user, acl_op.ACL_OP_DEL)
        except acl_op.AclError:
            failed.append(user)
            continue
    return failed


if __name__ == '__main__':
    pass
