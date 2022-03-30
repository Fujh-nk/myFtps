import os
from Server.src import statcode
from Server.src.ops import acl_op


def file_download(user, cwd, obj):
    """
    get the fd(rd mode) of obj file if user has property
    :param user: username
    :param cwd: current work dir
    :param obj: obj file
    :return: this operation status
    """
    if not acl_op.user_access(user, os.path.join(cwd, obj)):
        return statcode.SERVER_REJ, None
    try:
        fd = open(os.path.join(acl_op.WORK_REL_PATH, cwd, obj), 'rb')
    except OSError:
        return statcode.SERVER_ERR, None
    return statcode.SERVER_OK, fd


def file_upload(user, cwd, obj):
    """
    get the fd(wb mode) of obj file if user has property
    :param user: username
    :param cwd: current work dir
    :param obj: obj file
    :return: this operation status
    """
    if not acl_op.user_access(user, cwd):
        return statcode.SERVER_REJ, None
    try:
        fd = open(os.path.join(acl_op.WORK_REL_PATH, cwd, obj), 'wb')
    except OSError:
        return statcode.SERVER_ERR, None
    return statcode.SERVER_OK, fd


def file_del(user, cwd, obj):
    """
    delete obj file if user has property
    :param user: username
    :param cwd: current work dir
    :param obj: obj file
    :return: this operation status
    """
    if not acl_op.user_access(user, os.path.join(cwd, obj)):
        return statcode.SERVER_REJ
    try:
        os.remove(os.path.join(acl_op.WORK_REL_PATH, cwd, obj))
    except OSError:
        return statcode.SERVER_ERR
    return statcode.SERVER_OK


if __name__ == '__main__':
    os.chdir(r'..\.')
    file_del('test', 'test', '1.txt')
    pass
