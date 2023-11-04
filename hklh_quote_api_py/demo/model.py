# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import joblib
import time
import datetime
import pub
from pub import OP_BUY, OP_SELL, OP_NONE, POSITION_LONG, POSITION_SHORT
from pub import DIR_QUOTE, DIR_OPERATION, DIR_PREDICTION, QUOTE_COLUMNS
from pub import lg, ALL_CODES
from policy import Policy

cols_to_cal = ['open_price', 'close_price', 'vwap', 'volume']
used_dates = [1, 3, 5, 10, 30, 60, 90, 180]
used_minutes = [1, 3, 5, 10, 30, 60]

default_feat_rates_in_day = [.0] * (len(cols_to_cal) * len(used_minutes))

class FeatureBuilder():
    def __init__(self) -> None:
        # 每天更新的行情数据
        self.last_date = None
        self.last_time = None
        self.feat_dict_pre_days = dict()
        self.feat_dict_in_day = dict()

    def update_feat_pre_days(self, date):
        if self.last_date is not None and self.last_date >= date:
            return
        t1 = time.time()
        lg.info("---start to load history data")
        dfs = []
        df = pd.read_csv("history_quote\\test_data_for0901.csv")
        df.columns = QUOTE_COLUMNS
        dfs.append(df)

        for file in os.listdir(DIR_QUOTE):
            if file.endswith(".csv"):
                day = int(file.split('.')[0].split('_')[1])
                if day < date:
                    f = os.path.join(DIR_QUOTE, file)
                    df = pd.read_csv(f, header=None)
                    df.columns = QUOTE_COLUMNS
                    dfs.append(df)
        df = pd.concat(dfs)
        lg.info("---history data load end, dfcount: %s", len(df))
        used_dates_int = []
        for i in used_dates:
            used_dates_int.append(int(pub.get_pre_date(date, i)))
        print('used_dates_int: ', used_dates_int)
        df = df[df['date'].isin(used_dates_int)]
        df = df.dropna(axis=0, how='any')
        # df.to_csv('history_quote\\test_data_for0901.csv', index=False)

        df = df.set_index('hjcode', drop=True)
        df = df.sort_values(['date', 'times'], ascending=False)
        lg.info("---history data count: %s", len(df))
        # 每天的数据刷新后，调用
        self.feat_cal_days(df, date)
        self.last_date = date
        t2 = time.time()
        lg.info("---update_feat_pre_days consume: %.3f seconds", t2-t1)
        
    def update_feat_in_day(self, date, times):
        if self.last_time is not None:
            now = datetime.datetime.strptime(times, "%H%M%S")
            last = datetime.datetime.strptime(self.last_time, "%H%M%S")
            t_diff = (now - last).seconds
            if t_diff <= 60:
                return
        
        t1 = time.time()
        dfs = []
        for file in os.listdir(DIR_QUOTE):
            if file.endswith(".csv"):
                day = int(file.split('.')[0].split('_')[1])
                if day == date:
                    f = os.path.join(DIR_QUOTE, file)
                    df = pd.read_csv(f, header=None)
                    df.columns = QUOTE_COLUMNS
                    dfs.append(df)
        df = pd.concat(dfs)
        lg.info("df len: %s", len(df))
        if len(df) < 500*5:
            return
        df = df.dropna(axis=0, how='any')
        df = df.set_index('hjcode', drop=True)
        df = df.sort_values(['date', 'times'], ascending=False)
        self.feat_cal_in_day(df, date)
        self.last_time = times

        t2 = time.time()
        lg.info("---update_feat_in_day consume: %.3f seconds", t2-t1)

    # 每分钟数据刷新后, 调用
    def feat_cal_in_day(self, df, date):
        # df1 = df[df['date'].isin([date])]
        codes = df.index.unique()
        for code in codes:
            group = df.loc[code]
            df_day = group.set_index(['times'])
            times = df_day.index.unique()

            rows_pre = []
            try:
                for k in used_minutes:
                    # 此处跟离线处理有差异，此处从0开始是T-1
                    k = k - 1
                    col_values = [.0] * len(cols_to_cal)
                    if k < len(times):
                        pre_time = times[k]
                        # 第T-k时刻最后一条成交记录
                        row_pre = df_day.loc[pre_time].to_dict()
                        for ii, col in enumerate(cols_to_cal):
                            col_values[ii] = row_pre[col]
                    rows_pre.append(col_values)
            except Exception as e:
                print('df_day: ', df_day)
                print('row_pre: ', row_pre)
                raise e
            self.feat_dict_in_day[code] = rows_pre

    def feat_cal_days(self, df, date):
        # df1 = df[~df['date'].isin([date])]
        codes = df.index.unique()
        for code in codes:
            group = df.loc[code]
            g1 = group.set_index(['date'])
            days = g1.index.unique()

            # 前第N天的量价数据
            rows_pre = []
            for k in used_dates:
                pre_day = int(pub.get_pre_date(date, k))
                col_values = [.0] * len(cols_to_cal)
                if pre_day in days:
                    row_pre = g1.loc[pre_day].iloc[0]
                    for ii, col in enumerate(cols_to_cal):
                        col_values[ii] = row_pre[col]
                rows_pre.append(col_values)
            self.feat_dict_pre_days[code] = rows_pre
        

class LRModelPolicy(Policy):
    def __init__(self, date: int) -> None:
        super().__init__()
        self.model = joblib.load("./lr.pk")
        self.feature_builder = FeatureBuilder()
        self.feature_builder.update_feat_pre_days(date)
        self.tick_count = 0
        self.position_time = dict()

    def build_feature(self, tick):
        code = tick['hjcode']

        minute = int(int(tick['times']) / 100)
        feat_hour = [0]*4
        if minute >= 930 and minute < 1030:
            feat_hour[0] = 1
        elif minute >= 1030 and minute <= 1130:
            feat_hour[1] = 1
        elif minute >= 1300 and minute < 1400:
            feat_hour[2] = 1
        elif minute >= 1400 and minute <= 1500:
            feat_hour[3] = 1
        high_price_rate = tick['high_price'] / tick['open_price']
        low_price_rate = tick['low_price'] / tick['open_price']
        close_price_rate = tick['close_price'] / tick['open_price']
        vwap_rate = tick['vwap'] / tick['open_price']
        volume_log = np.log(tick['volume'])
        money_log = np.log(tick['money'])

        feat_rates_in_day = default_feat_rates_in_day
        # if code not in self.feature_builder.feat_dict_in_day:
        # else:
        #     feat_in_day = self.feature_builder.feat_dict_in_day[code]
        #     feat_rates_in_day = []
        #     for f in feat_in_day:
        #         rates = [.0] * len(cols_to_cal)
        #         for ii, col in enumerate(cols_to_cal):
        #             rates[ii] = f[ii] / tick[col]
        #         feat_rates_in_day.extend(rates)
        
        feat_days = self.feature_builder.feat_dict_pre_days[code]
        feats_rates_days = []
        try:
            for f in feat_days:
                rates = [.0] * len(cols_to_cal)
                for ii, col in enumerate(cols_to_cal):
                    rates[ii] = f[ii] / tick[col]
                feats_rates_days.extend(rates)
        except Exception as e:
            print('tick: ', tick)
            print('f: ', f)
            raise e

        example = []
        example.extend(feat_hour)
        example.extend([high_price_rate, low_price_rate, close_price_rate,
                        vwap_rate, volume_log, money_log])
        example.extend(feat_rates_in_day)
        example.extend(feats_rates_days)
        return example

    def predict(self, tick):
        self.tick_count += 1
        self.feature_builder.update_feat_pre_days(tick['date'])
        self.feature_builder.update_feat_in_day(tick['date'], tick['times'])

        example = self.build_feature(tick)
        pred_y = self.model.predict([example])[0]
        return pred_y, example
    
    def update(self):
        return super().update()
    
    def decide(self, tick):
        hjcode = tick['hjcode']
        op = OP_NONE
        if not self.check(tick):
            return op, 0, []

        dt = "{} {}".format(tick['date'], tick['times'])
        now = datetime.datetime.strptime(dt, '%Y%m%d %H%M%S')
        # 无持仓情况下
        if hjcode not in self.position:
            pred_y, example = self.predict(tick)
            if pred_y > 1:
                # 做多
                self.position[hjcode] = POSITION_LONG
                self.position_time[hjcode] = now
                op = OP_BUY
            elif pred_y < 1:
                # 做空
                self.position[hjcode] = POSITION_SHORT
                self.position_time[hjcode] = now
                op = OP_SELL
            return op, pred_y, example
        
        # 有持仓情况下，持仓超过10分钟即平仓
        t_diff = now - self.position_time[hjcode]
        if t_diff.seconds >= 10 * 60:
            op = - self.position[hjcode]
            del self.position[hjcode]
            del self.position_time[hjcode]
        return op, 0, []