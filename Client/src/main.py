import os.path

from mainwindow import Ui_MainWindow
from ftpclient import FtpClient
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication, QFileDialog
import sys
import socket
import ssl

VALID_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890_'
CERT_FILE = r'..\..\cert.pem'
KEY_FILE = r'..\..\key.pem'
WORK_DIR_ROOT = r'..\workspace'
SSL_VERSION = ssl.PROTOCOL_TLSv1
HOST = socket.gethostname()
PORT = 6666


def str_valid(_str):
    """
    judge if a str is valid or not
    :param _str: a string
    :return: a boolean
    """
    if len(_str) == 0:
        return False
    valid = True
    for ch in _str:
        if ch not in VALID_CHARS:
            valid = False
    return valid


class MyFuncBind:
    def __init__(self, ui, client):
        self.__ui = ui
        self.__client = client
        self.__cur_path = None

    def ui_init(self):
        self.__ui.tip_user.setText('User')
        self.__ui.edit_user.setText('')
        self.__ui.edit_passwd.setText('')
        self.__ui.obj_path.setText('Object File Path')
        self.__ui.cur_path.setText('Current Path')
        # for _ in range(self.__ui.cur_dir_list.count()):
        #     self.__ui.cur_dir_list.takeItem(0)
        self.__ui.cur_dir_list.clear()

    def btn_login_clicked(self):
        username = self.__ui.edit_user.text()
        if not str_valid(username):
            QMessageBox.information(MainWindow, 'Tips', 'Username invalid')
        password = self.__ui.edit_passwd.text()
        ok, msg = self.__client.login(username, password)
        if ok:
            self.__ui.tip_user.setText('User (logged in)')
            self.__ui.edit_passwd.setText('')
            self.__cur_path = '\\' + username
            self.__ui.cur_path.setText(self.__cur_path)
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_logout_clicked(self):
        ok, msg = self.__client.logout()
        if ok:
            self.ui_init()
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def __get_user_passwd(self):
        username = self.__ui.edit_user.text()
        if not str_valid(username):
            QMessageBox.information(MainWindow, 'Tips', 'Username invalid')
            return
        password = self.__ui.edit_passwd.text()
        if len(password) == 0:
            QMessageBox.information(MainWindow, 'Info', 'Please input password')
            return
        return username, password

    def btn_reg_clicked(self):
        username, password = self.__get_user_passwd()
        ok, msg = self.__client.reg_or_cancel(username, password, True)
        if ok:
            self.ui_init()
            QMessageBox.information(MainWindow, 'Info', 'Register ok, input again to log in')
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_cancel_clicked(self):
        username, password = self.__get_user_passwd()
        ok, msg = self.__client.login(username, password)[0]
        if not ok:
            QMessageBox.critical(MainWindow, 'Error', msg)
        if QMessageBox.question(MainWindow, 'Confirm', 'Are you sure to cancel user?') == QMessageBox.Yes:
            ok, msg = self.__client.reg_or_cancel(username, password, False)
            if ok:
                self.ui_init()
                QMessageBox.information(MainWindow, 'Info', 'Cancelled ok')
            else:
                QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_upload_clicked(self):
        path = self.__ui.obj_path.text()
        if not os.path.exists(path):
            QMessageBox.warning(MainWindow, 'Warning', 'Please select file first')
            return
        ok, msg = self.__client.upload(path)
        if ok:
            self.btn_refresh_clicked()
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def __set_list(self, content):
        self.__ui.cur_dir_list.clear()
        for _dir in content['dir']:
            self.__ui.cur_dir_list.addItem('(dir)-{}'.format(_dir))
        self.__ui.cur_dir_list.addItems(content['file'])

    def btn_refresh_clicked(self):
        ok, msg = self.__client.get_dir('')
        if ok:
            self.__set_list(msg)
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_cd_clicked(self):
        obj = self.__ui.cur_dir_list.selectedItems()[0].text()
        if '(dir)' not in obj:
            QMessageBox.critical(MainWindow, 'Error', 'Please select dir to cd')
            return
        ok, msg = self.__client.get_dir(obj[6:])
        if ok:
            self.__cur_path = os.path.join(self.__cur_path, obj)
            self.__ui.cur_path.setText(self.__cur_path)
            self.__set_list(msg)
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_new_dir_clicked(self):
        obj = self.__ui.name_input.text()
        if not str_valid(obj):
            QMessageBox.critical(MainWindow, 'Error', 'Dir name invalid')
            return
        ok, msg = self.__client.create_dir(obj)
        if ok:
            self.__ui.name_input.setText('')
            self.btn_refresh_clicked()
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_download_clicked(self):
        obj = self.__ui.cur_dir_list.selectedItems()[0].text()
        if '(dir)' in obj:
            QMessageBox.critical(MainWindow, 'Error', 'Please select file to download')
            return
        ok, msg = self.__client.download(obj)
        if ok:
            QMessageBox.information(MainWindow, 'Info', 'Download successfully')
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_delete_clicked(self):
        obj = self.__ui.cur_dir_list.selectedItems()[0].text()
        if '(dir)' in obj and QMessageBox.Yes == QMessageBox.question(MainWindow, 'Confirm',
                                                                      'Are you sure to delete dir'
                                                                      '(include all files in it)'):
            ok, msg = self.__client.delete(obj, 'DIR')
        else:
            ok, msg = self.__client.delete(obj, 'FILE')
        if ok:
            self.btn_refresh_clicked()
        else:
            QMessageBox.critical(MainWindow, 'Error', msg)

    def btn_files_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(MainWindow,
                                                   'select file',
                                                   WORK_DIR_ROOT,
                                                   'All Files (*)')
        self.__ui.obj_path.setText(file_path)

    def ui_bind_function(self):
        self.__ui.btn_download.clicked.connect(self.btn_download_clicked)
        self.__ui.btn_upload.clicked.connect(self.btn_upload_clicked)
        self.__ui.btn_del.clicked.connect(self.btn_delete_clicked)
        self.__ui.btn_new_dir.clicked.connect(self.btn_new_dir_clicked)
        self.__ui.btn_cd.clicked.connect(self.btn_cd_clicked)
        self.__ui.btn_files.clicked.connect(self.btn_files_clicked)
        self.__ui.btn_reflash.clicked.connect(self.btn_refresh_clicked)
        self.__ui.btn_login.clicked.connect(self.btn_login_clicked)
        self.__ui.btn_logout.clicked.connect(self.btn_logout_clicked)
        self.__ui.btn_cancel.clicked.connect(self.btn_cancel_clicked)
        self.__ui.btn_reg.clicked.connect(self.btn_reg_clicked)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    myfb = MyFuncBind(ui, FtpClient(HOST, PORT, CERT_FILE, KEY_FILE, SSL_VERSION))
    myfb.ui_bind_function()
    MainWindow.show()
    app.exec_()
