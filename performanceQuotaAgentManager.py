#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/3 下午4:37
# @Author  : Liujiaqi
# @Site    : 
# @File    : performanceQuotaAgentManager.py
# @Software: PyCharm

from daemon import Daemon
import sys, json
import logging
import os
import ConfigParser
from util.agentApiClient import AgentApiClient
import schedule
from mysqlPerformanceQuota.performanceQuota import PerformanceQuota

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
PIDFILE = BASEDIR+'/tmp/performanceAgent.pid'
LOGFILE = BASEDIR+'/logs/performanceAgent.log'

# Configure logging
logging.basicConfig(filename=LOGFILE, level=logging.DEBUG)

MODULENAME = 'performanceQuota'


class PerformanceQuotatDaemon(Daemon):

    quota = None
    apiClient = None
    instance_id = 0
    interval = 3

    def run(self):
        # 解析配置文件
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
        self.apiClient = AgentApiClient(api_url, MODULENAME)

        try:
            mysql_manage_info = self.apiClient.getCommonFun({'mysql_ip':mysql_ip,'mysql_port':mysql_port},'getMysqlManageInfo')
        except Exception, e:
            print e.message
            print "APIServer链接错误..."+"urtl="+str(self.apiClient.url)
            sys.exit()
        data_dict = eval(mysql_manage_info.text)
        print data_dict
        if data_dict.has_key('status_code') and data_dict['status_code'] == 500:
            print '获取mysqlPerformanceQuota配置失败,返回状态码:' + str(data_dict['return_code'])
            sys.exit()
        else:
            self.instance_id = data_dict['mysqlId']
            self.quota = PerformanceQuota(data_dict['manageUser'], data_dict['managePassword'], data_dict['mysqlHost'], int(data_dict['mysqlPort']),
                                          interval=self.interval)

            schedule.every(self.interval).seconds.do(self.postPerformanceData)
            while True:
                schedule.run_pending()

    def post_performance_data(self):

        post_data = self.quota.getPerformanceQuota()
        if post_data and self.instance_id != 0:
            try:
                print "发送数据到API"
                self.apiClient.postFun({'instance_id': self.instance_id, 'dataType':MODULENAME,'post_data': json.dumps(postData)})
            except Exception, e:
                print e.message

        else:
            print "instance_id = 0"




if __name__ == "__main__":

    daemon = PerformanceQuootatDaemon(PIDFILE)
    if len(sys.argv) == 2:

        if 'start' == sys.argv[1]:
            try:
                daemon.start()
            except:
                pass

        elif 'stop' == sys.argv[1]:
            print "PerformanceAgent Stopping ..."
            daemon.stop()

        elif 'restart' == sys.argv[1]:
            print "PerformanceAgent Restaring ..."
            daemon.restart()

        elif 'status' == sys.argv[1]:
            try:
                pf = file(PIDFILE, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None
            except SystemExit:
                pid = None

            if pid:
                print 'PerformanceAgent is running as pid %s' % pid
            else:
                print 'PerformanceAgent is not running.'

        else:
            print "Unknown command"
            sys.exit(2)
            sys.exit(0)
    else:
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)