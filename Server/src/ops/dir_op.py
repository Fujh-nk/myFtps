import os

from Server.src import statcode
from Server.src.ops import acl_op
import shutil


def dir_get(user, cwd):
    if not acl_op.user_access(user, cwd):
        return statcode.SERVER_REJ, None
    content = {'dir': [], 'file': []}
    obj_path = os.path.join(acl_op.WORK_REL_PATH, cwd)
    for item in os.listdir(obj_path):
        if os.path.isfile(os.path.join(obj_path, item)):
            content['file'].append(item)
        elif os.path.isdir(os.path.join(obj_path, item)):
            content['dir'].append(item)
    return statcode.SERVER_OK, content


def dir_create():
    pass


def dir_del():
    pass


if __name__ == '__main__':
    shutil.rmtree(r'..\..\workspace\test')
    pass
