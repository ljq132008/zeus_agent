#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/30 下午2:49
# @Author  : Liujiaqi
# @Site    : 
# @File    : DBUtil.py
# @Software: PyCharm
import MySQLdb
import logging

logger = logging.getLogger('logger01')


class DBUtil:

    def __init__(self):
        pass

    @staticmethod
    def get_connection(host, port, user, password):
        try:
            conn = MySQLdb.connect(host=host, port=int(port), user=user, passwd=password)
            return conn
        except MySQLdb.Warning, w:
            logger.warning("MySQL Warning:%s" % str(w))
            return conn
        except MySQLdb.Error, e:
            logger.error("MySQL Error:%s" % str(e))
            return conn
