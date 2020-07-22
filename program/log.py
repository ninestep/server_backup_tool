#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: zhangjun
# @Date  : 2018/7/26 9:20
# @Desc  : Description

import logging
import logging.handlers
import os
import time


class logs(object):
    def _initLog(self):
        self.logger = logging.getLogger("")
        # 设置输出的等级
        LEVELS = {'NOSET': logging.NOTSET,
                  'DEBUG': logging.DEBUG,
                  'INFO': logging.INFO,
                  'WARNING': logging.WARNING,
                  'ERROR': logging.ERROR,
                  'CRITICAL': logging.CRITICAL}
        # 创建文件目录
        logs_dir = "logs"
        if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
            pass
        else:
            os.mkdir(logs_dir)
        # 修改log保存位置
        timestamp = time.strftime("%Y-%m-%d", time.localtime())
        logfilename = '%s.txt' % timestamp
        logfilepath = os.path.join(logs_dir, logfilename)
        self.rotatingFileHandler = logging.handlers.RotatingFileHandler(filename=logfilepath,
                                                                        maxBytes=1024 * 1024 * 50,
                                                                        backupCount=5)
        # 设置输出格式
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        self.rotatingFileHandler.setFormatter(formatter)
        # 控制台句柄
        self.console = logging.StreamHandler()
        self.console.setLevel(logging.NOTSET)
        self.console.setFormatter(formatter)
        # 添加内容到日志句柄中
        self.logger.addHandler(self.rotatingFileHandler)
        self.logger.addHandler(self.console)
        self.logger.setLevel(logging.NOTSET)

    def _delLog(self):
        self.logger.removeHandler(self.rotatingFileHandler)
        self.logger.removeHandler(self.console)

    def info(self, message):
        self._initLog()
        self.logger.info(message)
        self._delLog()

    def debug(self, message):
        self._initLog()
        self.logger.debug(message)
        self._delLog()

    def warning(self, message):
        self._initLog()
        self.logger.warning(message)
        self._delLog()

    def error(self, message):
        self._initLog()
        self.logger.error(message)
        self._delLog()
