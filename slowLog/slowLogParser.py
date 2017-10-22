#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/25 下午9:50
# @Author  : Liujiaqi
# @Site    :
# @File    : slowLogParser.py
# @Software: PyCharm

import commands
import sys
import datetime
import re
import MySQLdb
from util.DBUtil import DBUtil
import SlowLogTail
import logging

logger = logging.getLogger('logger01')


class Parser:

    def __init__(self, mysql_id, api_client, interval, host, port, user, password):
        self.mysql_id = mysql_id
        self.fileName = Parser.get_slow_log_file(host, user, password, port)
        self.apiClient = api_client
        self.interval = interval

        self.event_dict = {}
        self.tmp_sql = []
        self.events = []

    # 获取mysql slow log文件名
    @staticmethod
    def get_slow_log_file(host, user, password, port):
        conn = None
        try:
            conn = DBUtil.get_connection(host, port, user, password)
        except MySQLdb.Error, e:
            logger.warning("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))

        cursor = conn.cursor()
        slow_log_file = "show variables like 'slow_query_log_file';"
        cursor.execute(slow_log_file)
        result = cursor.fetchone()
        print result[1]
        logger.debug('logfile_path='+str(result[1]))
        return result[1]

    def set_datetime_by_time_line(self, line):
        self.event_dict.clear()
        time_str = "20" + line.replace("# Time:", "").replace("  ", " ").strip()
        query_time = str(datetime.datetime.strptime(time_str, "%Y%m%d %H:%M:%S"))
        self.event_dict['time'] = query_time

    def set_query_info(self, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        tmp_items = tmp_line.split(" ")
        for tmp_item in tmp_items:
            if tmp_item.strip().startswith("Query_time:"):
                self.event_dict['query_time'] = tmp_item.replace("Query_time:", "")
            if tmp_item.strip().startswith("Lock_time:"):
                self.event_dict['lock_time'] = tmp_item.replace("Lock_time:", "")
            if tmp_item.strip().startswith("Rows_sent:"):
                self.event_dict['rows_sent'] = tmp_item.replace("Rows_sent:", "")
            if tmp_item.strip().startswith("Rows_examined:"):
                self.event_dict['rows_examined'] = tmp_item.replace("Rows_examined:", "")

    def set_login_user_ip(self, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        result = re.findall("\[([\S]+)\]", tmp_line)
        if len(result) == 1:
            self.event_dict['user'] = result[0]
            self.event_dict['ip'] = 'localhost'
        else:
            self.event_dict['user'] = result[0]
            self.event_dict['ip'] = result[1]

    def set_schema_error_killed(self, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        result = re.findall(":([\S]+)", tmp_line)
        if len(result) == 2:
            self.event_dict['schema'] = 'null'
            self.event_dict['last_error'] = result[0]
            self.event_dict['killed'] = result[1]
        else:
            self.event_dict['schema'] = result[0]
            self.event_dict['last_error'] = result[1]
            self.event_dict['killed'] = result[2]

    def set_bytes_sent(self, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        result = re.findall(":([\S]+)", tmp_line)
        self.event_dict['bytes_sent'] = result[0]

    def set_sql(self, line):
        if line.find(';') != -1:
            self.tmp_sql.append(line)
            full_sql = re.sub(r' {1,+}', " ", "".join(self.tmp_sql).replace("\n", " "))
            self.event_dict['sql'] = full_sql
            fingerprint_sql = commands.getstatusoutput("/usr/bin/pt-fingerprint --query '"+full_sql+"'")[1]
            self.event_dict['fingerprint'] = fingerprint_sql
            # 事件添加到events[]
            self.events.append(self.event_dict.copy())
            logger.debug(self.events)
            del self.tmp_sql[:]
            self.event_dict.clear()
        else:
            self.tmp_sql.append(line)

    def set_timestamp(self, line):
        result = re.findall("=([\S]+);", line)
        self.event_dict['timestamp'] = result[0]

    def paser_query_log(self, line):
        if line.startswith("# Time:"):
            self.set_datetime_by_time_line(line)
            # logger.debug("start with Time"+str(self.event_dict))
        elif line.startswith("# Query_time:"):
            self.set_query_info(line)
            # logger.debug("start with Time" + str(self.event_dict))
        elif line.startswith("# User@Host:"):
            self.set_login_user_ip(line)
            # logger.debug("start with Time" + str(self.event_dict))
        elif line.startswith("# Schema:"):
            self.set_schema_error_killed(line)
            # logger.debug("start with Time" + str(self.event_dict))
        elif line.startswith("# Bytes_sent:"):
            self.set_bytes_sent(line)
            # logger.debug("start with Time" + str(self.event_dict))
        elif line.startswith("SET timestamp"):
            self.set_timestamp(line)
            # logger.debug("start with Time" + str(self.event_dict))
        elif line.startswith("use "):
            pass
        else:
            self.set_sql(line)

    def slow_log_job_work(self, switch):
        logger.debug("开始监听slowlog...")
        print "开始监听slowlog..."
        if self.fileName:
            t = SlowLogTail.SlowTail(self.fileName)
            t.register_callback(self.paser_query_log)
            logger.debug("注册回调函数成功...")
            print "注册回调函数成功..."
            t.follow(interval=self.interval,
                     event_dict=self.event_dict,
                     tmp_sql=self.tmp_sql,
                     events=self.events,
                     mysql_instance_id=self.mysql_id,
                     api_client=self.apiClient,
                     switch=switch)
        else:
            logger.warning("慢日志文件不存在,监听慢日志程序退出....")
            sys.exit(0)
