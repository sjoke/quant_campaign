# -*- coding: utf-8 -*-

import sys
sys.path.append("..")
import os

from pub import OP_BUY, OP_SELL, OP_NONE
from recorder import Recorder
from policy import Policy
import datetime
from time import sleep
import time
from proto.type_pb2 import SDSDataType
from proto import type_pb2
from proto import message_pb2
from quote_api.quote_api import QuoteApi
from pub import lg

class QuoteImpl(QuoteApi):
    def __init__(self, ip, port, policy: Policy, 
                 recorder: Recorder, mode='remote'):
        QuoteApi.__init__(self, ip, port)
        self.login_success_ = False
        self.user = ''
        self.pwd = ''
        self.mac = ''
        self.policy = policy
        self.recorder = recorder
        self.mode = mode

    def onTick(self, tick):
        # 记录行情
        code = tick['hjcode']
        self.recorder.record_quote(tick)
        op, pred_y, features = self.policy.decide(tick)
        # lg.info('tick: %s', tick)
        # lg.info("decison: code: %s, op:%s, pred_y:%s", code, op, pred_y)

        if op == OP_BUY:
            lg.info("buy: %s", code)
            if self.mode == 'remote':
                self.buy(code)
            self.recorder.record_operation(tick, op, pred_y, features)
        elif op == OP_SELL:
            lg.info("sell: %s", code)
            if self.mode == 'remote':
                self.sell(code)
            self.recorder.record_operation(tick, op, pred_y, features)

    def setUserInfo(self, username, password):
        self.user = username
        self.pwd = password

    def isLogin(self):
        return self.login_success_

    def isConnected(self):
        return self.client.isConnected()

    def onMsg(self, msg):
        try:
            head = msg.head
            if head.msg_type == type_pb2.kMtLoginMegateAns:
                self.onLoginAns(msg)
            elif head.msg_type == type_pb2.kMtPublish:
                self.onPublish(msg)
        except Exception as e:
            print(e)

    def onPublish(self, msg):
        """订阅数据推送
        """
        for msg in self.message_buffer[msg.head.topic]:
            if (msg.head.topic == SDSDataType.KLN):
                kln = message_pb2.SDSKLine()
                kln.ParseFromString(msg.data)
                kline = {}
                timestamp = kln.timems / 1000
                dt = datetime.datetime.fromtimestamp(timestamp)
                kline['hjcode'] = kln.hjcode
                kline['date'] = int(dt.strftime("%Y%m%d"))
                kline['times'] = dt.strftime("%H%M%S")
                kline['open_price'] = kln.open*1.0/10000
                kline['high_price'] = kln.high*1.0/10000
                kline['low_price'] = kln.low*1.0/10000
                kline['close_price'] = kln.last*1.0/10000
                if kln.volume == 0:
                    kline['vwap'] = kline['open_price']
                else:
                    kline['vwap'] = kln.turnover*1.0/kln.volume/10000
                kline['money'] = kln.turnover
                kline['volume'] = kln.volume
                self.onTick(kline)
                # print("pub kln:",kln)

    def onConected(self, connected):
        if connected:
            print("connect success,try login")
            self.login(self.user, self.pwd, self.mac)
        else:
            print("connect loss")

    def onLoginAns(self, msg):
        """登录应答
        """
        login_ans = message_pb2.LoginAns()
        login_ans.ParseFromString(msg.data)
        if (login_ans.ret == login_ans.success):
            self.login_success_ = True
            print("login success")
        elif (login_ans.ret == login_ans.acc_error):
            print("acc error")
        elif (login_ans.ret == login_ans.not_login):
            print("账号已在别处登录！")
