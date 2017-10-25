#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/30 下午9:32
# @Author  : Liujiaqi
# @Site    : 
# @File    : performanceQuota.py
# @Software: PyCharm

import time
import MySQLdb
import schedule
import logging
logger = logging.getLogger('logger01')


class PerformanceQuota:

    def __init__(self, mysql_id, api_client, interval, mysql_host, mysql_port, mysql_user, mysql_password):
        self.mysql_id = mysql_id
        self.api_client = api_client
        self.user = mysql_user
        self.password = mysql_password
        self.quota_dict = {}
        self.host = mysql_host
        self.port = mysql_port
        self.interval = interval

        try:
            self.conn = MySQLdb.connect(host=self.host, port=int(self.port), user=self.user, passwd=self.password)
        except MySQLdb, e:
            print "Error %d:%s" % (e.args[0], e.args[1])
            exit(1)

    @staticmethod
    def now():
        # return str('2011-01-31 00:00:00')
        return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    @staticmethod
    def diff_dict(dict1, dict2, interval):
        r_dict = {}
        for k, v in dict1.iteritems():
            # 计算出interval时间内的各个参数的平均值,直接取整数部分
            r_dict[k] = int((int(v) - int(dict2[k])) / interval)
        return r_dict

    def get_performance_quota(self):
        tmp_dict = {}
        result_dict = {}
        self.conn.autocommit(True)
        cursor = self.conn.cursor()
        create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql = "show global status where Variable_name in ('Com_commit','com_delete','com_insert','Com_rollback','com_select','com_update','Questions');"
        cursor.execute(sql)
        results = cursor.fetchall()
        for quota in results:
            tmp_dict[quota[0]] = quota[1]

        if self.quota_dict:
            result_dict = self.diff_dict(tmp_dict, self.quota_dict, self.interval)
            self.quota_dict = tmp_dict.copy()
            result_dict['create_time'] = create_time
            logger.debug("result_dict="+str(result_dict))
            from util.apiFunName import FunNameDict
            self.api_client.agent_post(FunNameDict.PERFORMANCE_QUOTA, {'mysql_id': self.mysql_id, 'data': result_dict})
        # 如果quotaDict是空 则为第一次运行 将结果集赋值给全局quotaDict 不做任何处理
        else:
            self.quota_dict = tmp_dict.copy()
            logger.debug("init_dict" + str(result_dict))

    def performance_quota_job_work(self, switch):
        schedule.every(1).seconds.do(self.get_performance_quota)
        while switch.value:
            schedule.run_pending()

