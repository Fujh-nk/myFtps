import os
from Server.src import statcode
from Server.src.ops import acl_op
import shutil


def dir_get(user, cwd):
    """
    try to get file list in dir cwd
    :param user: username
    :param cwd: target dir path
    :return: this operation status and dir_list if it has
    """
    if not acl_op.user_access(user, cwd):
        return statcode.SERVER_REJ, None
    content = {'dir': [], 'file': []}
    obj_path = os.path.join(acl_op.WORK_REL_PATH, cwd)
    try:
        for item in os.listdir(obj_path):
            if os.path.isfile(os.path.join(obj_path, item)):
                content['file'].append(item)
            elif os.path.isdir(os.path.join(obj_path, item)):
                content['dir'].append(item)
    except OSError:
        return statcode.SERVER_ERR, None
    return statcode.SERVER_OK, content


def dir_create(user, cwd, obj):
    """
    create obj dir in dir cwd
    :param user: username
    :param cwd: current work dir
    :param obj: obj dir name
    :return: this operation status
    """
    if not acl_op.user_access(user, cwd):
        return statcode.SERVER_REJ
    obj_path = os.path.join(acl_op.WORK_REL_PATH, cwd, obj)
    try:
        os.mkdir(obj_path)
    except OSError:
        return statcode.SERVER_ERR
    return statcode.SERVER_OK


def dir_del(user, cwd, obj):
    """
    del obj dir includes all files and dirs in it
    :param user: username
    :param cwd: current work dir
    :param obj: obj dir name
    :return: this operation status
    """
    if not acl_op.user_access(user, cwd):
        return statcode.SERVER_REJ
    obj_path = os.path.join(acl_op.WORK_REL_PATH, cwd, obj)
    try:
        shutil.rmtree(obj_path)
    except OSError:
        return statcode.SERVER_ERR
    return statcode.SERVER_OK


if __name__ == '__main__':
    os.chdir(r'..\.')
    # shutil.rmtree(r'..\..\workspace\test')
    print(dir_get('test', 'test'))
    dir_del('test', 'test', 'abc')
    pass
