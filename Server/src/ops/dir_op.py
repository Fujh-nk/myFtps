import Server.src.statcode
from acl_op import user_access
import shutil


def dir_get(user, cwd):
    if user_access(user, cwd):
        pass
    return


def dir_create():
    pass


def dir_del():
    pass


if __name__ == '__main__':
    shutil.rmtree(r'..\..\workspace\test')
    pass
