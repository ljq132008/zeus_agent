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
import os
from util.Tail import Tail

logger = logging.getLogger('logger01')


class SlowTail(Tail):

    last_file_size = -1
    current_file_size = -1

    def follow(self, **kwargs):
        """
        Do a tail follow. If a callback function is registered it is called with every new line.
        Else printed to standard out.

        Arguments:
            s - Number of seconds to wait between each iteration; Defaults to 1.
        """

        with open(self.tailed_file) as file_:
            # Go to the end of file
            file_.seek(0, 2)
            while kwargs['switch'].value:
                self.current_file_size = os.path.getsize(self.tailed_file)
                curr_position = file_.tell()
                line = file_.readline()
                if not line:
                    file_.seek(curr_position)
                    if kwargs['events']:
                        slow_log_events_list = kwargs['events']
                        logger.debug(slow_log_events_list)
                        instance_id = kwargs['mysql_instance_id']
                        # 发送post请求

                        try:
                            logger.debug("发送数据到API")
                            post_client = kwargs['api_client']
                            from util.apiFunName import FunNameDict
                            post_client.agent_post(FunNameDict.PUSH_SLOW_LOGS, {'mysql_id': instance_id, 'data': slow_log_events_list})
                        except Exception, e:
                            print e.message
                            logger.error("发送post请求失败...继续监听slowlog")

                    del kwargs['events'][:]

                    if self.current_file_size < self.last_file_size:
                        file_.seek(0, 2)
                    time.sleep(kwargs['interval'])
                    self.last_file_size = self.current_file_size
                else:
                    self.callback(line)
