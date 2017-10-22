#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/30 下午9:32
# @Author  : Liujiaqi
# @Site    : 
# @File    : PerformanceQuota.py
# @Software: PyCharm

import time
import MySQLdb
import schedule


class PerformanceQuota:

    def __init__(self, mysql_user, mysql_password, mysql_host, mysql_port, interval):
        self.user = mysql_user
        self.password = mysql_password
        self.quotaDict = {}
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

    def diffDict(self,dict1,dict2,interval):
        rDict = {}
        for k,v in dict1.iteritems():
            # 计算出interval时间内的各个参数的平均值,直接取整数部分
            rDict[k] = int((int(v) - int(dict2[k])) / interval)
        return rDict


    def getPerformanceQuota(self):
        tmpDict = {}
        resultDict = {}
        self.conn.autocommit(True)
        cursor = self.conn.cursor()
        create_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        sql = "show global status where Variable_name in ('Com_commit','com_delete','com_insert','Com_rollback','com_select','com_update','Questions');"
        cursor.execute(sql)
        results = cursor.fetchall()
        for quota in results:
            tmpDict[quota[0]] = quota[1]

        if self.quotaDict:
            print self.quotaDict
            print tmpDict
            resultDict = self.diffDict(tmpDict,self.quotaDict,self.interval)
            self.quotaDict = tmpDict.copy()
            resultDict['create_time'] = create_time
            print "resultDict="+str(resultDict)

            return resultDict
        # 如果quotaDict是空 则为第一次运行 将结果集赋值给全局quotaDict 不做任何处理
        else:
            self.quotaDict = tmpDict.copy()
            print "inittDict" + str(resultDict)
            return resultDict

if __name__ == '__main__':
    quota = PerformanceQuota('root','123465','192.168.1.104',3306)

    schedule.every(1).seconds.do(quota.getPerformanceQuota)
    while True:
        schedule.run_pending()