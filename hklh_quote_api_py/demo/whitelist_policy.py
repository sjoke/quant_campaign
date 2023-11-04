# -*- coding: utf-8 -*-
import os
import datetime
import random
import pandas as pd
from policy import Policy
from pub import OP_BUY, OP_SELL, OP_NONE, POSITION_LONG, POSITION_SHORT
'''
随机买入或者卖出,持有10分钟后平仓
'''


class WhitelistPolicy(Policy):
    def __init__(self) -> None:
        super().__init__()
        self.position_time = dict()
        self.hjcode_level = {}
        self.load_whitelist()

    def load_whitelist(self):
        #stock_weight_level.csv
        # schema: code-weight-level
        # level#1: weight<0.15,
        # level#2: weight>=0.15&&weight<0.25
        # level#3: weight>=0.25
        df = pd.read_csv('../stock_weight_level.csv')
        for idx, row in df.iterrows():
            self.hjcode_level[row['code']] = row['level']

    def get_stock_level(self, hjcode):
        if hjcode in self.hjcode_level.keys():
            return self.hjcode_level[hjcode]
        else:
            return 2

    def decide(self, tick):
        hjcode = tick['hjcode']
        op = OP_NONE

        dt = "{} {}".format(tick['date'], tick['times'])
        now = datetime.datetime.strptime(dt, '%Y%m%d %H%M%S')
        # 无持仓情况下
        if hjcode not in self.position:
            if hjcode in self.hjcode_level.keys():
                # 做多
                self.position[hjcode] = POSITION_LONG
                self.position_time[hjcode] = now
                op = OP_BUY
                return op, 0, []
            else:
                return OP_NONE, 0, []

        # 有持仓情况下，持仓超过10分钟即平仓
        t_diff = now - self.position_time[hjcode]
        if t_diff.seconds >= 10 * 60:
            op = - self.position[hjcode]
            del self.position[hjcode]
            del self.position_time[hjcode]
        return op, 0, []
