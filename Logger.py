#!/home/tops/bin/python
# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = 'default.log'


def init_logger(log, log_file=LOG_FILE):
    logger = logging.getLogger(log)
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)  # 实例化formatter
    handler.setFormatter(formatter)  # 为handler添加formatter
    logger.addHandler(handler)  # 为logger添加handler
    logger.setLevel(logging.DEBUG)
    return logger
