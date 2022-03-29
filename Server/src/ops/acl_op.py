import os
import subprocess
import ntsecuritycon
import win32security


WORK_REL_PATH = r'..\..\workspace'
ACL_OP_ADD = 'add'
ACL_OP_DEL = 'del'


class AclError(Exception):
    pass


class DenyError(AclError):
    pass


class FailError(AclError):
    pass


def _add_dacl(user):
    """
    add user access property on user's root path
    :param user: username
    :return: None
    """
    sid, domain, stype = win32security.LookupAccountName(None, user)
    _path = os.path.join(WORK_REL_PATH, user)
    sd = win32security.GetFileSecurity(_path, win32security.DACL_SECURITY_INFORMATION)
    dacl = sd.GetSecurityDescriptorDacl()
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, 3, ntsecuritycon.FILE_ALL_ACCESS, sid)
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(_path, win32security.DACL_SECURITY_INFORMATION, sd)


def acl_user(user, op):
    """
    add or del net user at local host
    :param user: username
    :param op: add or del
    :return: None
    """
    sp = subprocess.Popen(
        'net user {} /{}'.format(user, op),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stderr = str(sp.stderr.read().decode("gbk")).strip()
    stdout = str(sp.stdout.read().decode("gbk")).strip()
    if "" != stderr:
        raise DenyError
    if stdout.find("失败") > -1:
        raise FailError()

    if op == ACL_OP_ADD:
        try:
            _add_dacl(user)
        except Exception:
            subprocess.Popen(
                'net user {} /del'.format(user),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            raise FailError()


def _access(user, abspath):
    """
    judge if user can access abspath or not
    :param user: username
    :param abspath: the absolute file path
    :return: a boolean
    """
    sd = win32security.GetFileSecurity(abspath, win32security.DACL_SECURITY_INFORMATION)
    dacl = sd.GetSecurityDescriptorDacl()
    for i in range(dacl.GetAceCount()):
        rev, access, t_sid = dacl.GetAce(i)
        try:
            t_user = win32security.LookupAccountSid('', t_sid)[0]
        except Exception:
            continue
        if t_user == user:
            return True
    return False


def user_access(user, cwd):
    """
    judge if user has the property to access cwd
    :param user: username
    :param cwd: the target path wanted, cwd is a relative path
    :return: a boolean
    """
    user_root = os.path.join(WORK_REL_PATH, user)
    abspath = os.path.join(WORK_REL_PATH, cwd)
    if user_root not in abspath:
        return _access(user, abspath)
    return _access(user, user_root)


if __name__ == '__main__':
    acl_user('test', ACL_OP_ADD)
    print(user_access('test', os.path.join(WORK_REL_PATH, 'test')))
    print(user_access('test', os.path.join(WORK_REL_PATH, r'test\1.txt')))
    pass
