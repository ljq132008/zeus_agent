#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/26 下午5:48
# @Author  : Liujiaqi
# @Site    : 
# @File    : agentDaemon.py
# @Software: PyCharm

from daemon import Daemon
import json
import os
import time
import logging
from logging.config import fileConfig
import multiprocessing
import ConfigParser
from multiprocessing import Value
from util.agentApiClient import AgentApiClient
from util.apiFunName import FunNameDict

# todo 写入配置文件
BASEDIR = os.getcwd()
PIDFILE = BASEDIR+'/tmp/Agent.pid'

# 初始化logging
fileConfig('logging.conf')
logger = logging.getLogger('logger01')


class MonitorProcess:
    def __init__(self, name, monitor_type, status, a_process):
        self.name = name
        self.monitor_type = monitor_type
        self.status = status
        self.a_process = a_process
        logger.debug('MonitorProcess init name='+str(MonitorProcess)+',monitor_type='+self.monitor_type+',status='+str(self.status.value))

    def set_status_off(self):
        self.status.value = False

    def get_status(self):
        if self.a_process and self.a_process.is_alive():
            return True
        else:
            return False

    def set_process(self, a_process):
        self.a_process = a_process


class AgentManager(Daemon):

    def __init__(self):
        Daemon.__init__(self, pidfile=PIDFILE, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
        # 初始化agent相关变量
        config = ConfigParser.ConfigParser()
        config.read(BASEDIR+'/zeus_agent.conf')
        self.agent_ip = config.get("zeus_agent", "agent_ip")
        # 保存启动的所有进程k为监控名字_ip_port
        self.processDict = {}
        self.apiUrl = config.get("zeus_agent", "api_server")
        self.agentApiClient = AgentApiClient(self.apiUrl)
        logger.info('AgentManager初始化完毕，api server:'+str(self.apiUrl))

    def run(self):
        # todo
        while True:
            """
            #通过api请求 zeus 的服务器配置
            #获取服务器IP的所有端口mysql监控配置,
            #通过api 发送各个实例的监控情况发送到zeus处理
            #拉取配置文件处理
            """
            monitor_conf = self.agentApiClient.agent_post(FunNameDict.GET_MONITOR_CONF, {'host_ip': self.agent_ip})
            # logger.debug("monitor_conf="+str(monitor_conf.text))
            self.decode_monitor_config(json.loads(monitor_conf.text))
            # post当前processDict中各个进程的监控状态
            time.sleep(3)

    # 传入一个response的数据 list
    def decode_monitor_config(self, response_data):
        logger.debug("processDict="+str(self.processDict))
        for a_mysql_monitor_conf in response_data:
            conf_dict_name = self.replace_com(a_mysql_monitor_conf['ip'])+"_"+str(a_mysql_monitor_conf['port'])
            logger.debug(conf_dict_name)
            if a_mysql_monitor_conf['configs']:
                # 有监控配置项进行处理
                for monitorType in a_mysql_monitor_conf['configs']:
                    for k, v in monitorType.iteritems():
                        # 判断是否存在于processDict ，存在说明监控已开启
                        dict_key = conf_dict_name+"_"+str(k)
                        logger.debug("dict_key="+str(dict_key))
                        if self.processDict.has_key(dict_key):
                            # 如果有说明已经有过这个监控进程，判断是与现在的状态一样，不一样更新为最新取到的状态
                            monitor_obj = self.processDict[dict_key]
                            if monitor_obj.get_status() and v:
                                # 监控状态和获取的zeus的状态都是 开启(True) 不做处理
                                logger.debug(str(dict_key) + ':状态一致不做处理')
                                continue
                            else:
                                if v:
                                    # 如果zeus 为开启 那么说明 当前监控是关闭的，开启监控进程
                                    # 构建一个新进程覆盖原来的 MonitorProcess.aProcess
                                    logger.info(str(dict_key) + ':监控线程重新开启')
                                    self.processDict[dict_key] = AgentManager.get_type_process(k,
                                                                                               dict_key,
                                                                                               a_mysql_monitor_conf['id'],
                                                                                               self.agentApiClient,
                                                                                               a_mysql_monitor_conf['ip'],
                                                                                               a_mysql_monitor_conf['port'],
                                                                                               a_mysql_monitor_conf['user'],
                                                                                               a_mysql_monitor_conf['password'])
                                else:
                                    # 如果zeus 为关闭 那么说明当前监控为开启，关闭监控进程
                                    logger.info(str(monitor_obj.name)+':监控线程被关闭')
                                    monitor_obj.set_status_off()
                                    monitor_obj.set_process(None)
                        else:
                            # 没有开启过监控，判断返回数据是否开启监控
                            if v:
                                logger.debug(str(dict_key)+'监控进程创建并开启')
                                # 构建一个新进程 赋给 processDict
                                self.processDict[dict_key] = AgentManager.get_type_process(k,
                                                                                           dict_key,
                                                                                           a_mysql_monitor_conf['id'],
                                                                                           self.agentApiClient,
                                                                                           a_mysql_monitor_conf['ip'],
                                                                                           a_mysql_monitor_conf['port'],
                                                                                           a_mysql_monitor_conf['user'],
                                                                                           a_mysql_monitor_conf['password'])
                            else:
                                # 进程字典中不存在，获取的状态为关闭 不做处理直接跳过
                                logger.debug('进程字典中不存在，获取的状态为关闭 不做处理直接跳过')
                                continue
            else:
                # 这个mysql实例没有配置任何获取数据配置项跳过
                continue

    @staticmethod
    def get_type_process(monitor_type, dict_key, mysql_id, api_client, mysql_host, mysql_port,
                         mysql_user, mysql_password):

        if monitor_type == 'slowlog':
            logger.info(str(dict_key) + ':监控线程准备创建')
            logger.debug(monitor_type)
            a_process = AgentManager.get_slow_log_process(dict_key, monitor_type, mysql_id, api_client, mysql_host, mysql_port, mysql_user, mysql_password)
            return a_process
        elif monitor_type == 'performance_quota':
            logger.info(str(dict_key) + ':监控线程准备创建')
            logger.debug(monitor_type)
            a_process = AgentManager.get_performance_quota_process(dict_key, monitor_type, mysql_id, api_client, mysql_host, mysql_port, mysql_user, mysql_password)
            return a_process
        else:
            # todo
            pass

    @staticmethod
    def replace_com(ip):
        ip_str = str(ip)
        return ip_str.replace('.', '_')

    @staticmethod
    def get_slow_log_process(name, monitor_type, mysql_id, api_client, mysql_host, mysql_port, mysql_user, mysql_password):
        from slowLog.slowLogParser import Parser
        handler = Parser(mysql_id, api_client, 3, mysql_host, mysql_port, mysql_user, mysql_password)
        logger.debug("slow log handler 被创建")
        switch = Value('b', True)
        a_process = multiprocessing.Process(target=handler.slow_log_job_work, args=(switch,))
        a_process.start()
        logger.debug("slow log 监控进程被创建")
        return MonitorProcess(name, monitor_type, switch, a_process)

    @staticmethod
    def get_performance_quota_process(name, monitor_type, mysql_id, api_client, mysql_host, mysql_port, mysql_user, mysql_password):
        from mysqlPerformanceQuota.performanceQuota import PerformanceQuota
        handler = PerformanceQuota(mysql_id, api_client, 1, mysql_host, mysql_port, mysql_user, mysql_password)
        logger.debug("performance quota handler 被创建")
        switch = Value('b', True)
        a_process = multiprocessing.Process(target=handler.performance_quota_job_work, args=(switch,))
        a_process.start()
        logger.debug("performance quota 监控进程被创建")
        return MonitorProcess(name, monitor_type, switch, a_process)

    @staticmethod
    def test_process(switch, name):
        logger.debug("switch="+str(switch))
        while switch.value:
            logger.debug(str(name)+"........")
            time.sleep(2)

if __name__ == "__main__":

    agent = AgentManager()
    agent.run()
    """
    daemon = AgentManager(PIDFILE)
    if len(sys.argv) == 2:

        if 'start' == sys.argv[1]:
            try:
                daemon.start()
            except:
                pass

        elif 'stop' == sys.argv[1]:
            print "Agent Stopping ..."
            daemon.stop()

        elif 'restart' == sys.argv[1]:
            print "Agent Restaring ..."
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
    """