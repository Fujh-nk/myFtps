import logging
import os
from logging import handlers

LOG_FILE_PATH = '../log'


class MyLogger:
    __my_logger = None

    @staticmethod
    def __create():
        MyLogger.__my_logger = logging.getLogger('MyLogger')
        MyLogger.__my_logger.setLevel(logging.DEBUG)
        my_formatter = logging.Formatter('%(asctime)s -- %(levelname)s: %(message)s')

        stream_handle = logging.StreamHandler()
        stream_handle.setLevel(logging.ERROR)
        stream_handle.setFormatter(my_formatter)
        MyLogger.__my_logger.addHandler(stream_handle)

        file_handle = handlers.TimedRotatingFileHandler(filename=os.path.join(LOG_FILE_PATH, 'myFtps.log'), when='D')
        file_handle.setLevel(logging.INFO)
        file_handle.setFormatter(my_formatter)
        MyLogger.__my_logger.addHandler(file_handle)

    @staticmethod
    def debug(msg):
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.debug(msg)

    @staticmethod
    def info(msg):
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.info(msg)

    @staticmethod
    def warning(msg):
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.warning(msg)

    @staticmethod
    def error(msg):
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.error(msg)

    @staticmethod
    def critical(msg):
        if MyLogger.__my_logger is None:
            MyLogger.__create()
        MyLogger.__my_logger.critical(msg)


if __name__ == '__main__':
    MyLogger.info('ab')
    MyLogger.error('aaa')
    MyLogger.warning('ab')
    MyLogger.debug('aaa')
    MyLogger.critical('aaa')
