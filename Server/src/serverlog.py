import os
import logging
from logging import handlers

LOG_FILE_PATH = '../log'


class MyLogger:
    __my_logger = None

    @staticmethod
    def __create():
        """
        create a custom logger object:
        a console logger handler for level error and above logging
        a file logger handler for level info and above logging
        :return: None
        """
        MyLogger.__my_logger = logging.getLogger('MyLogger')
        MyLogger.__my_logger.setLevel(logging.DEBUG)
        my_formatter = logging.Formatter('%(asctime)s -- %(levelname)s: %(message)s')

        # add a console logger handler for level error and above logging
        stream_handle = logging.StreamHandler()
        stream_handle.setLevel(logging.ERROR)
        stream_handle.setFormatter(my_formatter)
        MyLogger.__my_logger.addHandler(stream_handle)

        # add a file logger handler for level info and above logging
        file_handle = handlers.TimedRotatingFileHandler(filename=os.path.join(LOG_FILE_PATH, 'myFtps.log'), when='D')
        file_handle.setLevel(logging.INFO)
        file_handle.setFormatter(my_formatter)
        MyLogger.__my_logger.addHandler(file_handle)

    @staticmethod
    def debug(msg):
        """
        custom debug logging
        :param msg: logging message
        :return: None
        """
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.debug(msg)

    @staticmethod
    def info(msg):
        """
        custom info logging
        :param msg: logging message
        :return: None
        """
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.info(msg)

    @staticmethod
    def warning(msg):
        """
        custom warning logging
        :param msg: logging message
        :return: None
        """
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.warning(msg)

    @staticmethod
    def error(msg):
        """
        custom error logging
        :param msg: logging message
        :return: None
        """
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.error(msg)

    @staticmethod
    def critical(msg):
        """
        custom critical logging
        :param msg: logging message
        :return: None
        """
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.critical(msg)


if __name__ == '__main__':
    MyLogger.info('ab')
    MyLogger.error('aaa')
    MyLogger.warning('ab')
    MyLogger.debug('aaa')
    MyLogger.critical('aaa')
