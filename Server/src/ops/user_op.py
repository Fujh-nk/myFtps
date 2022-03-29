import userdb_op
import acl_op


def username_valid(username):
    valid = True
    for ch in username:
        if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_':
            valid = False
    return valid


def user_reg(user, passwd):
    status = userdb_op.add_user(user, passwd)
    if status == userdb_op.STATUS_OK:
        try:
            acl_op.acl_user(user, acl_op.ACL_OP_ADD)
        except acl_op.AclError:
            status = userdb_op.STATUS_FAILED
    return status


def user_login(user, passwd):
    return userdb_op.check_user_passwd(user, passwd)


def user_del(user, passwd):
    status = userdb_op.check_user_passwd(user, passwd)
    if status == userdb_op.STATUS_OK:
        status = userdb_op.cancel_user(user)
    return status


def user_release():
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
