# -*- coding: utf-8 -*-
import os
import sys
import datetime
import logging as lg
import json

OP_NONE = 0
OP_BUY = 1
OP_SELL = -1

POSITION_LONG = 1
POSITION_SHORT = -1


QUOTE_COLUMNS = ['hjcode', 'date', 'times', 'open_price', 'high_price',
                 'low_price', 'close_price', 'vwap', 'money', 'volume']

QUOTE_CSV_COLUMNS = ['code', 'date', 'times', 'open_price', 'high_price',
                     'low_price', 'close_price', 'vwap', 'money', 'volume']

DIR_QUOTE = 'quotes'
DIR_OPERATION = 'operations'
DIR_PREDICTION = 'predictions'


lg.basicConfig(level=lg.INFO,
               format='%(asctime)s.%(msecs)03d %(levelname)s ' +
               '%(filename)s:%(lineno)d: %(message)s',
               datefmt='%Y-%m-%d %H:%M:%S',
               filename='./stdout.log',
               filemode='w',
               )


def lg_qps(cnt, end, start):
    t = (end - start).seconds
    if t <= 0:
        t = 1
    lg.info("qps: %f", 1.0 * cnt / t)


def get_pre_date(date, n_day, fmt='%Y%m%d'):
    cur_date = datetime.datetime.strptime(str(date), fmt)
    pre_date = cur_date - datetime.timedelta(days=n_day)
    return pre_date.strftime(fmt)


def get_pre_minute(date, n_day, fmt='%Y%m%d'):
    cur_date = datetime.datetime.strptime(date, fmt)
    pre_date = cur_date - datetime.timedelta(days=n_day)
    return pre_date.strftime(fmt)


f = os.path.join('history_quote', 'all_codes.txt')
with open(f, 'r') as fp:
    ALL_CODES = json.load(fp)