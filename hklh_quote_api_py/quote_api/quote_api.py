from .tcp_client import TcpClient
from .qtp_msg import QtpMsg

import os, sys,time
sys.path.append("..")

from proto import message_pb2
from proto import type_pb2
import time
import threading,queue

HKLH_QUOTE_API_VERSION = "2.3.14"


class QuoteApi:
    def __init__(self, ip, port):
        self.client = TcpClient()
        self.ip = ip
        self.port = port
        self.run_ = True
        # self.client.setConnectCallback(self.onConected)
        self.last_connect_status = False
        self.batchSize = {}
        self.interval = {}
        self.last_processed_time = {}
        self.message_buffer = {}  # 用于缓存订阅消息的列表


    def stop(self):
        self.run_ = False
        self.client.stop()

    def run(self):
        threading.Thread(target=self.loop).start()
        threading.Thread(target=self.client.recv_data).start()

    def buy(self, hjcode):
        self.send_order(True,hjcode)

    def sell(self, hjcode):
        self.send_order(False,hjcode)

    def send_order(self,is_buy:bool, hjcode):
        msg = QtpMsg()
        msg.head.msg_type = 1000
        msg.head.version = 1
        data = "{},{}".format(hjcode,'B' if is_buy else 'S')
        msg.set_data(data.encode())
        self.client.send_data(msg.encode())

    def login(self, acc, pwd, mac):
        msg = QtpMsg()
        msg.head.msg_type = type_pb2.kMtLoginMegate
        msg.head.version = 1
        login_req = message_pb2.LoginRequest()
        login_req.acc = acc
        login_req.pwd = pwd
        login_req.mac = mac

        msg.set_data(data=login_req.SerializeToString())
        self.client.send_data(msg.encode())

    def unsub(self, topic, codes):
        msg = QtpMsg()
        msg.head.msg_type = type_pb2.kMtUnsubscribe
        msg.head.version = 1
        msg.head.topic = topic
        sub = message_pb2.SDSUnSubscribe()

        for item in codes:
            sub.hjcode.append(item)
        print("unsub ",topic," ",codes)
        msg.set_data(data=sub.SerializeToString())
        self.client.send_data(msg.encode())

    def set_topic_poll_params(self,topic,batchSize,interval):
        self.batchSize[topic] = batchSize
        self.interval[topic] = interval

    def sub(self, topic, codes):
        msg = QtpMsg()
        msg.head.msg_type = type_pb2.kMtSubscribe
        msg.head.version = 1
        msg.head.topic = topic
        sub = message_pb2.SDSubscribe()
        print("sub ",topic," ",codes)
        for item in codes:
            sub.hjcode.append(item)

        msg.set_data(data=sub.SerializeToString())
        self.client.send_data(msg.encode())
        self.last_processed_time[topic] = time.time() * 1000

    def pubCustomData(self, topic, key, value):
        msg = QtpMsg()
        msg.head.msg_type = type_pb2.kMtCustomMsgPub
        msg.head.topic = topic
        msg.head.version = 1
        sub = message_pb2.SDSCustomData()
        sub.topic =  topic
        sub.key = key
        sub.value = value
        now = int(time.time() * 1000) 
        sub.timems = now
        print("pub ",topic," ",key)
        msg.set_data(data=sub.SerializeToString())
        self.client.send_data(msg.encode())

    def queryCache(self, topic, codes):
        msg = QtpMsg()
        msg.head.msg_type = type_pb2.kMtQueryCode
        msg.head.version = 1
        msg.head.topic = topic
        query = message_pb2.QueryCode()
        for item in codes:
            query.hjcode.append(item)

        msg.set_data(data=query.SerializeToString())
        self.client.send_data(msg.encode())

    def querySecureMaster(self, last_update_time=0):
        msg = QtpMsg()
        msg.head.msg_type = type_pb2.kMtGetSecuMasterV2
        msg.head.version = 1
        msg.head.topic = 0
        query = message_pb2.SecureMasterRequest()
        query.time = last_update_time
        msg.set_data(data=query.SerializeToString())
        self.client.send_data(msg.encode())

    def sendHeartBeat(self):
        msg = QtpMsg()
        msg.head.msg_type = type_pb2.kMtHeartBeat
        msg.head.version = 1
        msg.head.topic = 0
        msg.set_data(data="")
        self.client.send_data(msg.encode())

    def beforeMsg(self,msg):
        if msg.head.msg_type == type_pb2.kMtPublish:
            # 添加接收消息到缓存
            if msg.head.topic not in self.message_buffer:
                tmp_json = []
                tmp_json.append(msg)
                self.message_buffer.update({msg.head.topic:tmp_json})
            else:
                self.message_buffer[msg.head.topic].append(msg)

            if msg.head.topic not in self.batchSize:
                self.batchSize[msg.head.topic] = 1
            if msg.head.topic not in self.interval:
                self.interval[msg.head.topic] = 0
            current_time = time.time() * 1000
            # 当缓存消息数量达到 batchSize 或达到间隔时，批量处理和打印
            if len(self.message_buffer[msg.head.topic]) >= self.batchSize[msg.head.topic] or (self.interval[msg.head.topic] > 0 and current_time - self.last_processed_time[msg.head.topic] >= self.interval[msg.head.topic]):
                if len(self.message_buffer[msg.head.topic]) > 0:
                    self.onMsg(msg)
                    del self.message_buffer[msg.head.topic]# 清空消息缓冲
                self.last_processed_time[msg.head.topic] = current_time
        else:
            self.onMsg(msg)

    def onMsg(self, msg):
        pass

    def onConected(self,connected):
        print("on api connect:",connected)
        pass


    def checkConnectStatus(self):
        if self.last_connect_status != self.client.isConnected():
            self.last_connect_status = self.client.isConnected()
            self.onConected(self.last_connect_status)

    def loop(self):
        while self.run_:
            if self.client.isConnected() == False:
                self.client.run(self.ip, self.port)
                time.sleep(3)
            else:
                try:
                    msg = self.client.q_.get(block=True,timeout=3)
                    self.beforeMsg(msg)
                except Exception as e:
                    self.sendHeartBeat()
            self.checkConnectStatus()

                    
