#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/26 下午4:01
# @Author  : Liujiaqi
# @Site    : 
# @File    : agentApiClient.py
# @Software: PyCharm

import requests
import json


class AgentApiClient:

    def __init__(self, url):
        self.url = url

    def agent_post(self, fun_name, parameters):
        return requests.post(self.url, data={'funName': fun_name, 'parameters': json.dumps(parameters)})

if __name__ == '__main__':
    api = AgentApiClient('http://10.20.0.155:5001/api/v1000/agent')
    try:
        monitor_confs = api.agent_post('getMonitorConf', "{'host_ip':'10.20.0.254'}")
        print monitor_confs.text

    except Exception as error:
        print "链接APIServer出错"+error.message