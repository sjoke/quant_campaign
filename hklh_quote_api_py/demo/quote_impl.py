import os, sys
sys.path.append("..")
from quote_api.quote_api import QuoteApi
from proto import message_pb2
from proto import type_pb2
from proto.type_pb2 import SDSDataType
import time
from time import sleep
import datetime
import json
import logging
import joblib

logging.basicConfig(level=logging.INFO,
                    filename='./stockholding.log',
                    filemode='a',
                    format='[%(asctime)s] [%(levelname)s] - %(message)s')


class StockHolding:
    def __init__(self):
        self.stock_volumn = {}

    def add(self, code, buy_price):
        if code not in self.stock_volumn.keys():
            # 买入1手
            tmp = {}
            tmp['volumn'] = 1
            tmp['buy_price'] = buy_price
            self.stock_volumn[code] = tmp
            logging.info(code + "|buy|" + buy_price + "|" + json.dumps(self.stock_volumn))
        else:
            if self.stock_volumn[code]['volumn'] == -1:
                # 买入平仓，数量清0，计算收益率
                self.stock_volumn[code]['volumn'] = 0
                self.stock_volumn[code]['rate_return'] = 0
                logging.info(code + "|buy|" + buy_price + "|" + json.dumps(self.stock_volumn))
            else:
                # 不能买入，最多买入1手
                logging.info(code + "|buy|" + buy_price + "|already holding, cannot buy." + json.dumps(self.stock_volumn))

    def remove(self, code, sell_price):
        if code not in self.stock_volumn.keys():
            # 卖空1手
            tmp = {}
            tmp['volumn'] = -1
            tmp['sell_price'] = sell_price
            self.stock_volumn[code] = tmp
            logging.info(code + "|sell|" + sell_price + "|" + json.dumps(self.stock_volumn))
        else:
            if self.stock_volumn[code]['volumn'] == 1:
                # 卖出平仓，数量清0，计算收益率
                self.stock_volumn[code]['volumn'] = 0
                self.stock_volumn[code]['rate_return'] = 0
                logging.info(code + "|sell|" + sell_price + "|" + json.dumps(self.stock_volumn))
            else:
                # 不能卖出，最多卖空1手
                logging.info(code + "|sell|" + sell_price + "|already holding, cannot sell." + json.dumps(self.stock_volumn))

class QuoteImpl(QuoteApi):
    def __init__(self, ip, port):
        QuoteApi.__init__(self, ip, port)
        self.login_success_ = False
        self.user = ''
        self.pwd = ''
        self.mac = ''
        self.stock_position = 0.0
        self.stock_holding = StockHolding()
        self.model = ''
        self.features = {}
        self.stock_info = {}

    def setUserInfo(self,username,password):
         self.user = username
         self.pwd = password

    def setModel(self, model_dir):
        self.model = joblib.load(model_dir)

    def setFeature(self, offline_feature_dir):
        # 假设特征格式id:features
        # 例如：002463.SZ:0.1,0.2,0.3,...
        with open(offline_feature_dir, 'r') as f:
            for line in f:
                line_arr = line.split(":")
                self.features[line_arr[0]] = line_arr[1]

    def setStockInfo(self, stock_info_dir):
        # 假设仅有行业信息，例如002463.SZ:新能源
        with open(stock_info_dir, 'r') as f:
            for line in f:
                line_arr = line.split(":")
                self.stock_info[line_arr[0]] = line_arr[1]

    def isLogin(self):
        return self.login_success_

    def isConnected(self):
        return self.client.isConnected()


    def onMsg(self,msg):
        try:
            head = msg.head
            print("-msg_type:{} -topic:{} -type_pb2:{} -version:{} -service:{} -opt_len:{} -data_len:{}".format(head.msg_type, head.topic, type_pb2.kMtLoginMegateAns, head.version, head.service, head.opt_len, head.data_len))
            if head.msg_type == type_pb2.kMtLoginMegateAns:
                self.onLoginAns(msg)
            elif head.msg_type == type_pb2.kMtPublish:
                self.onPublish(msg)
        except Exception as e:
            print(e)

    def query(self, topic, codes):
        self.api_.queryCache(self, topic, codes)

    def predict(self, tick):
        # 拼接预测样本
        stock_features = self.features[tick['hjcode']]
        real_features = [0.1,0.2,0.3]
        pred_features = stock_features + real_features
        # 预测下一时刻的vwap
        vwap_pred = self.model.predict(pred_features)
        return vwap_pred

    def onTick(self,tick):
        # print("onTick: {}".format(tick))
        # print(tick)
        logging.info("realtime data | " + tick)

        # 策略1：过滤行业
        stock_industry = self.stock_info[tick['hjcode']]
        if stock_industry == '':
            logging.info('{}|{}, invalid stock, give up buy or sell'.format(tick['hjcode'], stock_industry))
            return

        # 策略2, 判断下一时刻的交易价超出昨天收盘价
        # 预测下一时刻的vwap
        vwap_pred = self.predict(tick)
        if vwap_pred > tick['close_price']:
            self.buy(tick['hjcode'])
            self.stock_holding.remove(tick['hjcode'], tick['vwap'])
        else:
            self.buy(tick['hjcode'])
            self.stock_holding.add(tick['hjcode'], tick['vwap'])

        # # 交易策略，待补充
        # if tick['close_price'] >tick['vwap']:
        #     self.sell(tick['hjcode'])
        #     self.stock_holding.remove(tick['hjcode'], tick['vwap'])
        # else:
        #     self.buy(tick['hjcode'])
        #     self.stock_holding.add(tick['hjcode'], tick['vwap'])

    def onSub(self, msg):
        self.onSub(msg.head)

    def onPublish(self,msg):
        """订阅数据推送
        """
        for msg in self.message_buffer[msg.head.topic]:
            if(msg.head.topic == SDSDataType.KLN):
                kln = message_pb2.SDSKLine()
                kln.ParseFromString(msg.data)
                kline = {}
                timestamp = kln.timems / 1000
                dt = datetime.datetime.fromtimestamp(timestamp)
                kline['hjcode'] = kln.hjcode
                kline['date'] = int(dt.strftime("%Y%m%d"))
                kline['times'] = int(dt.strftime("%H%M%S"))
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

    def onConected(self,connected):
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
        if(login_ans.ret == login_ans.success):
            self.login_success_ = True
            print("login success")
        elif(login_ans.ret == login_ans.acc_error):
            print("acc error")
        elif(login_ans.ret == login_ans.not_login):
            print("账号已在别处登录！")

