# -*- coding: utf-8 -*-
import os
from models import Model
from pub import OP_BUY, OP_SELL, OP_NONE, POSITION_LONG, POSITION_SHORT


class Policy():
    def __init__(self) -> None:
        self.model = Model()
        self.position = dict()
        self.trade_record_dir = 'trade_records'

    def run(self):
        # 1.获取实时行情

        # 2.构造特征

        # 3.输入模型

        # 4.结合模型预测结果，做交易决策

        pass

    def record_trade(self, date, time, hjcode, op):
        f = os.path.join(self.trade_record_dir, "trade_{}.csv".format(date))
        with open(f, 'a') as fp:
            line = "{}{},{},{}".format(date, time, hjcode, op)
            fp.write(line)


    def decide(self, tick):
        hjcode = tick['hjcode']
        # 构造特征，模型预测
        # 专家经验
        # 结合持仓判断是否支持买卖
        current_dt = '{}{}'.format(tick['date'], tick['times'])
        op = OP_NONE
        if hjcode == '002025.SZ':
            if hjcode not in self.position or self.position[hjcode] != POSITION_LONG:
                # buy
                self.position[hjcode] = POSITION_LONG
                op = OP_BUY
            else:
                op = OP_SELL
        if hjcode == '000739.SZ':
            if hjcode not in self.position or self.position[hjcode] != POSITION_SHORT:
                # sell
                self.position[hjcode] = POSITION_SHORT
                op = OP_SELL
            else:
                op = OP_BUY
        return op