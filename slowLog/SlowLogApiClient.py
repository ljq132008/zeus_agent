#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/26 下午4:01
# @Author  : Liujiaqi
# @Site    : 
# @File    : SlowLogApiClient.py
# @Software: PyCharm

import slowLog.Parser
import logging
import sys

import requests
from util.LoggerUtil import Logger

logger = Logger('slowlogagent.log',logging.DEBUG,logging.DEBUG)


class GetSlowLogApiClient():

    def __init__(self,ip,port,url):
        self.ip = ip
        self.port = port
        self.url = url+"?ip=%s&port=%s" % (self.ip,self.port)

    def get_mysql_conf(self):
        mysql_group_list_data = requests.get(self.url)
        data = mysql_group_list_data.json()
        if data:
            return data

