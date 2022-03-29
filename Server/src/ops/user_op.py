import Server.src.statcode


def username_valid(username):
    valid = True
    for ch in username:
        if ch not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_':
            valid = False
    return valid


def user_reg(user, passwd):
    pass


def user_login(user, passwd):
    pass


def user_del(user, passwd):
    pass


if __name__ == '__main__':
    pass
