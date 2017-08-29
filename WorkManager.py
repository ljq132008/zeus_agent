'''
1.不需要do_job方法，通过work_manager.add_job来发布任务给线程池
2.线程中Queue.get需要block
3.task_done方法是配合Queue.join使用的，这里应该不需要
4.任务执行成功后把执行结果放在done_queue中
5.方法的注释应该写在函数名的下面。
'''
import threading
import time
import traceback

import queue


class Worker(threading.Thread):
    def __init__(self, work_manager):
        threading.Thread.__init__(self)
        self.work_queue = work_manager.work_queue
        self.done_queue = work_manager.done_queue
        self.start()

    def run(self):
        while True:
            try:
                do, arg, kwargs = self.work_queue.get(block=True)
                result = do(*arg, **kwargs)
                self.done_queue.put((do, arg, result))
            except Exception as e:
                print(traceback.format_exc())
                print(self.getName(), "end", str(e))
                break


class WorkManager(object):
    def __init__(self, thread_num=2):
        self.work_queue = queue.Queue()  # 队列对象
        self.done_queue = queue.Queue()  # 执行完成的任务
        self.threads = []
        self._init_thread_pool(thread_num)

    def _init_thread_pool(self, thread_num):
        """初始化线程"""
        for i in range(thread_num):
            worker = Worker(self)
            self.threads.append(worker)

    def add_job(self, job, arg=[], kwargs={}):
        """初始化工作队列"""
        self.work_queue.put((job, arg, kwargs))

def getSlowLogEvent():
    while True:
        print("send a slow log event....")
        time.sleep(1)

def getEerroLogEvent():
    while True:
        print("send a error log event....")
        time.sleep(1)

work_manager = WorkManager()
work_manager.add_job(getSlowLogEvent, [])
work_manager.add_job(getEerroLogEvent, [])
time.sleep(1)
while not work_manager.done_queue.empty():
    print(work_manager.done_queue.get(False))
