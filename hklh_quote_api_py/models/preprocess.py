# -*- coding: utf-8 -*-

'''
每天运行, 生成天级别特征并保存为文件,
T日线上使用前, 先Load进内存
T-1日特征用于T日
'''

import os
import pandas as pd
import numpy as np

cols_to_cal = ['open_price', 'close_price', 'vwap', 'volume']


class OfflineFeature():
    def __init__(self, data_dir_days: str, data_dir_in_day: str) -> None:
        # 天级别离线交易数据
        self.data_dir_days = data_dir_days
        # 日内交易数据, 分钟级别
        self.data_dir_in_day = data_dir_in_day
        self.feat_dict_pre_days = dict()
        self.feat_dict_in_day = dict()
        pass

    def preprocess(self, df):
        df1 = df.dropna(axis=0, how='any')
        df1 = df1.set_index('code')
        codes = df1.index.unique()
        df1 = df1.sort_values(['date', 'times'], ascending=False)
        return df1, codes

    # 每分钟数据刷新后, 调用

    def feat_cal_in_day(self):
        df = pd.read_csv(self.data_dir_in_day)
        df1, codes = self.preprocess(df)

        for code in codes:
            group = df1.loc[code]
            df_day = group.set_index(['times'])
            times = df_day.index.unique()

            rows_pre = []
            for k in [1, 3, 5, 10, 30, 60]:
                # 此处跟离线处理有差异，此处从0开始是T-1天
                k = k - 1
                col_values = [.0] * len(cols_to_cal)
                if k < len(times):
                    pre_time = times[k]
                    # 第T-k时刻最后一条成交记录
                    row_pre = df_day.loc[pre_time].iloc[0]
                    for ii, col in enumerate(cols_to_cal):
                        col_values[ii] = row_pre[col]
                rows_pre.append(col_values)
            self.feat_dict_in_day[code] = rows_pre

    # 每天的数据刷新后，调用
    def feat_cal_pre_days(self):
        df = pd.read_csv(self.data_dir_days)
        df1, codes = self.preprocess(df)

        for code in codes:
            group = df1.loc[code]
            g1 = group.set_index(['date', 'times'])
            days = g1.index.get_level_values(0).unique()

            # 前第N天的量价数据
            rows_pre = []
            for k in [1, 3, 5, 10, 30, 60, 90, 180]:
                # 此处跟离线处理有差异，此处从0开始是T-1天
                k = k - 1
                col_values = [.0] * len(cols_to_cal)
                if k < len(days):
                    pre_day = days[k]
                    # 第T-k天最后一条成交记录
                    row_pre = g1.loc[pre_day].iloc[0]
                    for ii, col in enumerate(cols_to_cal):
                        col_values[ii] = row_pre[col]
                rows_pre.append(col_values)
            self.feat_dict_pre_days[code] = rows_pre
