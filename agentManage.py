#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/27 下午7:04
# @Author  : Liujiaqi
# @Site    : 
# @File    : agentManage.py
# @Software: PyCharm
import ConfigParser
import logging
import sys

from slowLog.SlowLogApiClient import GetSlowLogApiClient
from slowLog.Parser import Parser
from util.LoggerUtil import Logger

logger = Logger('slowlogagent.log',logging.DEBUG,logging.DEBUG)

def main():
    print __file__+"main()"
    # 获取要获取slowlog的mysql ip 和 端口
    cp = ConfigParser.SafeConfigParser()
    cp.read('slowLog.conf')
    selections = cp.sections()
    mysql_ip = cp.get('db1', 'mysql_ip')
    mysql_port = cp.get('db1', 'mysql_port')
    api_url = cp.get('db1', 'api_server_url')

    slowConf = GetSlowLogApiClient(mysql_ip, mysql_port, api_url)
    try:
        confParametersDict = slowConf.get_mysql_conf()
    except Exception, e:
        print e.message
        logger.error("APIServer链接错误...")
        sys.exit()


    if confParametersDict.has_key('status_code') and confParametersDict['status_code'] == 500:
        logger.error('获取mysql慢日志配置失败,返回状态码:' + str(confParametersDict['return_code']))
        sys.exit()
    else:
        intervalValue = 3
        eventDic = {}
        tmpSQL = []
        events = []
        print type(events)

        # 获取实例slowlog配置信息
        mysql_instance_id = confParametersDict['id']
        mysql_slow_log = confParametersDict['slow_query_log']
        mysql_slow_log_file = confParametersDict['slow_query_log_file']

        if mysql_slow_log == 'ON':
            handler = Parser(interval=intervalValue, eventDic=eventDic, tmpSQL=tmpSQL, events=events,
                                           mysqlId=mysql_instance_id, fileName=mysql_slow_log_file, apiUrl=api_url)
            logger.debug(str(__file__)+"slowlog Parser 初始化完毕...")
            print str(__file__)+"slowlog Parser 初始化完毕..."

            handler.slowLogJobWork()
        else:
            logger.error(str(mysql_ip) + ":" + str(mysql_port) + "mysql实例slowlog未开启,不能获取慢日志")
            sys.exit()


if __name__ == '__main__':
    main()