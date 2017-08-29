#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/25 下午9:50
# @Author  : Liujiaqi
# @Site    :
# @File    : Parser.py
# @Software: PyCharm

import commands
import datetime
import logging
import re

from util.LoggerUtil import  Logger
import SlowLogTail

logger = Logger('slowlogagent.log',logging.DEBUG,logging.DEBUG)

class Parser():

    def __init__(self,interval=3,eventDic={},tmpSQL=[],events=[],mysqlId=0,fileName='',apiUrl='',count=0):
        self.interval = interval
        self.eventDic = eventDic
        self.tmpSQL = tmpSQL
        self.events = events
        self.mysqlId = mysqlId
        self.fileName = fileName
        self.apiUrl = apiUrl
        self.count = count

    def set_datetime_by_time_line(self,eventDic, line):
        eventDic.clear()
        time_str = "20" + line.replace("# Time:", "").replace("  ", " ").strip()
        query_time = str(datetime.datetime.strptime(time_str, "%Y%m%d %H:%M:%S"))
        eventDic['time'] = query_time

    def set_query_info(self,eventDic, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        tmp_items = tmp_line.split(" ")
        for tmp_item in tmp_items:
            if tmp_item.strip().startswith("Query_time:"):
                eventDic['query_time'] = tmp_item.replace("Query_time:", "")
            if tmp_item.strip().startswith("Lock_time:"):
                eventDic['lock_time'] = tmp_item.replace("Lock_time:", "")
            if tmp_item.strip().startswith("Rows_sent:"):
                eventDic['rows_sent'] = tmp_item.replace("Rows_sent:", "")
            if tmp_item.strip().startswith("Rows_examined:"):
                eventDic['rows_examined'] = tmp_item.replace("Rows_examined:", "")

    def set_login_user_ip(self,eventDic, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        result = re.findall("\[([\S]+)\]", tmp_line)
        if len(result) == 1:
            eventDic['user'] = result[0]
            eventDic['ip'] = 'localhost'
        else:
            eventDic['user'] = result[0]
            eventDic['ip'] = result[1]

    def set_schema_error_killed(self,eventDic, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        result = re.findall(":([\S]+)", tmp_line)
        if len(result)==2:
            eventDic['schema'] = 'null'
            eventDic['last_errno'] = result[0]
            eventDic['killed'] = result[1]
        else:
            eventDic['schema'] = result[0]
            eventDic['last_errno'] = result[1]
            eventDic['killed'] = result[2]

    def set_bytes_sent(self,eventDic, line):
        tmp_line = line.replace("#", "").replace(": ", ":").replace("  ", " ").replace("  ", " ")
        result = re.findall(":([\S]+)", tmp_line)
        eventDic['bytes_sent'] = result[0]

    def set_sql(self,eventDic, line, tmpSQL,events):
        if line.find(';') != -1:
            fullSQL=""
            tmpSQL.append(line)
            fullSQL=re.sub(r' {1,}'," ","".join(tmpSQL).replace("\n"," "))
            eventDic['sql'] = fullSQL
            fingerprintSQL=commands.getstatusoutput("/usr/bin/pt-fingerprint --query '"+fullSQL+"'")[1]
            eventDic['fingerprint'] = fingerprintSQL
            #事件添加到events[]
            events.append(eventDic.copy())
            logger.debug(events)
            del tmpSQL[:]
            eventDic.clear()
        else:
            tmpSQL.append(line)

    def set_timestamp(self,eventDic, line):
        result = re.findall("=([\S]+);", line)
        eventDic['timestamp'] = result[0]

    def paserQueryLog(self,line,kwargs):
        if line.startswith("# Time:"):
            self.set_datetime_by_time_line(kwargs['eventDic'], line)
            logger.debug("start with Time"+str(kwargs['eventDic']))
        elif line.startswith("# Query_time:"):
            self.set_query_info(kwargs['eventDic'], line)
            logger.debug("start with Time" + str(kwargs['eventDic']))
        elif line.startswith("# User@Host:"):
            self.set_login_user_ip(kwargs['eventDic'], line)
            logger.debug("start with Time" + str(kwargs['eventDic']))
        elif line.startswith("# Schema:"):
            self.set_schema_error_killed(kwargs['eventDic'], line)
            logger.debug("start with Time" + str(kwargs['eventDic']))
        elif line.startswith("# Bytes_sent:"):
            self.set_bytes_sent(kwargs['eventDic'], line)
            logger.debug("start with Time" + str(kwargs['eventDic']))
        elif line.startswith("SET timestamp"):
            self.set_timestamp(kwargs['eventDic'], line)
            logger.debug("start with Time" + str(kwargs['eventDic']))
        elif line.startswith("use "):
            pass
        else:
            self.set_sql(kwargs['eventDic'], line, kwargs['tmpSQL'],kwargs['events'])
            logger.debug("start with Time" + str(kwargs['eventDic'])+":"+str(kwargs['tmpSQL'])+":"+str(kwargs['events']))


    def slowLogJobWork(self):
        logger.debug(str(__file__) + "开始监听slowlog...")
        print str(__file__) + "开始监听slowlog..."
        t = SlowLogTail.slowTail(self.fileName)
        t.register_callback(self.paserQueryLog)
        logger.debug(str(__file__) + "注册回调函数成功...")
        print str(__file__) + "注册回调函数成功..."
        t.follow(interval=self.interval,eventDic=self.eventDic,tmpSQL=self.tmpSQL,events=self.events,mysql_instance_id=self.mysqlId,apiUrl=self.apiUrl)
