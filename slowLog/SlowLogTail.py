#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/25 下午9:50
# @Author  : Liujiaqi
# @Site    :
# @File    : SlowLogTail.py
# @Software: PyCharm

import logging
import time
import json

from util.LoggerUtil import Logger
from util.Tail import Tail
import requests

logger = Logger('slowlogagent.log',logging.DEBUG,logging.DEBUG)

class PostSlowLogApiClient():

    def __init__(self,url,data):
        self.url = url
        self.data = data

    def post_slow_log_data(self):
        request = requests.post(self.url,self.data)
        logger.debug("slow log发送服务器端 postData:"+str(self.data))

class slowTail(Tail):

    def follow(self,**kwargs):
        ''' Do a tail follow. If a callback function is registered it is called with every new line. 
        Else printed to standard out.

        Arguments:
            s - Number of seconds to wait between each iteration; Defaults to 1. '''

        with open(self.tailed_file) as file_:
            # Go to the end of file
            file_.seek(0, 2)
            while True:
                curr_position = file_.tell()
                line = file_.readline()
                #logger.debug(line)
                if not line:
                    file_.seek(curr_position)
                    logger.debug(str(__file__ )+" "+str(kwargs['events']))
                    if kwargs['events']:
                        slowLogEventsList = kwargs['events']
                        instance_id = kwargs['mysql_instance_id']
                        #通过API发送到服务器端处理
                        apiUrl = kwargs['apiUrl']
                        #发送post请求
                        try:
                            print "发送数据到API"
                            postClient = PostSlowLogApiClient(apiUrl,{'instance_id':instance_id,'post_data':json.dumps(slowLogEventsList)})
                            postClient.post_slow_log_data()
                        except Exception, e:
                            print e.message
                            logger.error("发送post请求失败...继续监听slowlog")
                    del kwargs['events'][:]
                    time.sleep(kwargs['interval'])
                else:
                    self.callback(line,kwargs)