# -*- coding: utf-8 -*-
import os
import datetime
import random
from policy import Policy
from pub import OP_BUY, OP_SELL, OP_NONE, POSITION_LONG, POSITION_SHORT
from pub import DIR_QUOTE, DIR_OPERATION, DIR_PREDICTION, QUOTE_COLUMNS
from pub import lg, ALL_CODES



'''
随机买入或者卖出,持有10分钟后平仓
'''
class RandomPolicy(Policy):
    def __init__(self) -> None:
        super().__init__()
        self.position_time = dict()
        
    def decide(self, tick):
        hjcode = tick['hjcode']
        op = OP_NONE

        dt = "{} {}".format(tick['date'], tick['times'])
        now = datetime.datetime.strptime(dt, '%Y%m%d %H%M%S')
        # 无持仓情况下
        if hjcode not in self.position:
            pred_y = random.random()
            if pred_y >= 0.5:
                # 做多
                self.position[hjcode] = POSITION_LONG
                self.position_time[hjcode] = now
                op = OP_BUY
            else:
                # 做空
                self.position[hjcode] = POSITION_SHORT
                self.position_time[hjcode] = now
                op = OP_SELL
            return op, pred_y, []
        
        # 有持仓情况下，持仓超过10分钟即平仓
        t_diff = now - self.position_time[hjcode]
        if t_diff.seconds >= 10 * 60:
            op = - self.position[hjcode]
            del self.position[hjcode]
            del self.position_time[hjcode]
        return op, 0, []
