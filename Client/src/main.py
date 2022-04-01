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
    valid = True
    for ch in _str:
        if ch not in VALID_CHARS:
            valid = False
    return valid


class MyFuncBind:
    def __init__(self, ui, client):
        self.__ui = ui
        self.__client = client
        self.__list_items = None

    def get_edit_text(self, _edit):
        pass

    def get_selected_item(self):
        pass

    def btn_login_clicked(self):
        QMessageBox.critical(MainWindow, 'Error', 'error')
        pass

    def btn_logout_clicked(self):
        pass

    def btn_reg_clicked(self):
        pass

    def btn_cancel_clicked(self):
        pass

    def btn_upload_clicked(self):
        pass

    def btn_refresh_clicked(self):
        pass

    def btn_cd_clicked(self):
        pass

    def btn_new_dir_clicked(self):
        pass

    def btn_download_clicked(self):
        pass

    def btn_delete_clicked(self):
        pass

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
    # QMessageBox.critical(MainWindow, 'Error', 'error')
    app.exec_()
