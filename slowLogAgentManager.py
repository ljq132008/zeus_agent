#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/2 上午12:08
# @Author  : Liujiaqi
# @Site    : 
# @File    : slowLogAgentManager.py
# @Software: PyCharm

from daemon import Daemon
import logging
import os
from slowLog.slowLogParser import Parser

"""
负责管理agent节点
1、根据agentConf.conf配置文件初始化相关参数:
    [common]:服务器通用配置
        api_server: post数据的api服务器(不同模块post数据会带不同的flag，服务器端根据flag调用相关处理方法)
    [db?]:服务器存在的mysql实例序列
        mysql_ip：服务器IP
        mysql_port: mysql实例端口
        slowLog_interval: 慢日志获取周期
        performance_quota_interval: 性能参数获取周期
2、根据api_server初始化一个agent api client对象 包含get 和 post 方法调用函数
    get方法通过getDataType参数传递要获取相应数据
    解析get获取到的数据：
        statusCode:200 表示成功 非 200 表示获取数据出错 返回数据为 {statusCode:xxxx,errorCode:xxxx,errorMessage:xxxx}
3、将实例化的 api client对象 传入各个模块初始化参数使用
"""

BASEDIR = os.getcwd()
print BASEDIR
AGENTCONFIGFILE = BASEDIR+'/zeus_agent.conf'
PIDFILE = BASEDIR+'/tmp/slowLogAgent.pid'
LOGFILE = BASEDIR+'/logs/slowLogAgent.log'

# Configure logging
logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)

MODULENAME = 'slowlog'



class SlowLogAgentDaemon(Daemon):
    """

    def run(self):
        #解析配置文件
        cp = ConfigParser.SafeConfigParser()
        if not os.path.exists(AGENTCONFIGFILE):
            print AGENTCONFIGFILE
            print "agent配置文件不存在"
            sys.exit(1)
        cp.read(AGENTCONFIGFILE)
        print "sections:"+str(cp.sections())
        mysql_ip = cp.get('db1', 'mysql_ip')
        mysql_port = cp.get('db1', 'mysql_port')
        api_url = cp.get('db1', 'api_server_url')

        apiClient = AgentApiClient(api_url, MODULENAME)

        try:
            confParametersDict = apiClient.getCommonFun({'mysql_ip':mysql_ip,'mysql_port':mysql_port},'getMysqlConf')
        except Exception, e:
            print e.message
            print "APIServer链接错误..."+"urtl="+str(apiClient.url)
            sys.exit()
        dataDict = eval(confParametersDict.text)
        if dataDict.has_key('status_code') and dataDict['status_code'] == 500:
            print '获取mysql慢日志配置失败,返回状态码:' + str(dataDict['return_code'])
            sys.exit()
        else:
            intervalValue = 3
            eventDic = {}
            tmpSQL = []
            events = []

            # 获取实例slowlog配置信息
            mysql_instance_id = dataDict['id']
            mysql_slow_log = dataDict['slow_query_log']
            mysql_slow_log_file = dataDict['slow_query_log_file']

            if mysql_slow_log == 'ON':
                handler = Parser(interval=intervalValue, eventDic=eventDic, tmpSQL=tmpSQL, events=events,
                                        mysqlId=mysql_instance_id, fileName=mysql_slow_log_file, apiUrl=api_url,apiClient=apiClient)
                print str(__file__) + "slowlog Parser 初始化完毕..."
                handler.slowLogJobWork()
            else:
                print str(mysql_ip) + ":" + str(mysql_port) + "mysql实例slowlog未开启,不能获取慢日志"
                sys.exit()
    """

if __name__ == "__main__":
    handler = Parser(1, None, 3, '10.20.0.254', 3306, 'root', '123465')
    from multiprocessing import Valueß
    switch = Value('b', True)
    handler.slow_log_job_work(switch)
