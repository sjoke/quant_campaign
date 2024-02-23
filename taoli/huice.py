import json
from binance.spot import Spot
from binance.um_futures import UMFutures
from binance.cm_futures import CMFutures
import time
import os
import pandas as pd
from tqdm import tqdm
import datetime
from typing import Union
import json
import paux
import argparse
import util
from util import lg
import schedule
from typing import Sequence
import argparse


spot_client = Spot()
um_futures_client = UMFutures()
cm_futures_client = CMFutures()
print('spot_client ping: ',  spot_client.ping())
print('um_futures_client ping: ',  um_futures_client.ping())


def exchange_info():
    res = cm_futures_client.exchange_info()
    # with open('futures_cm_all.json', 'w') as fp:
    #     json.dump(res, fp)

    delivery_prods = [s for s in res['symbols'] if s['contractType'] not in ['', 'PERPETUAL', 'PERPETUAL_DELIVERING']]
    with open('futures_delivery_cm.json', 'w') as fp:
        json.dump(delivery_prods, fp)


def is_month_end(date: datetime.datetime):
    t = date + datetime.timedelta(days=7)
    return date.month != t.month


def get_future_delivery_date(date: datetime.datetime) -> Sequence[datetime.datetime]:
    # 季度合约，每个自然季度月的最后一个星期五，08:00:00 UTC
    # 交割价格：交割前最后1小时，每秒现货价格的平均值
    # binance: 当季/次季
    # okex: 当周/次周，当月/次月,当季/次季
    delivery_dates = [None] * 2
    # 当季
    for i in range(1, 100, 1):
        day = date + datetime.timedelta(days=i)
        # 月末周五
        if day.weekday() == 4 and is_month_end(day) and day.month in [3, 6, 9, 12]:
            delivery_dates[0] = day
            break
    # 次季
    for i in range(7, 100, 7):
        day = delivery_dates[0] + datetime.timedelta(days=i)
        # 月末周五
        if is_month_end(day) and day.month in [3, 6, 9, 12]:
            delivery_dates[1] = day
            break
    return delivery_dates


# 下载某一天多产品历史K线数据
def download_candles_by_date(symbol, date: datetime.date, bar):
    global spot_client
    # 日期时间对象，其中小时分钟秒均为0
    # 起始毫秒时间戳
    start_ts = int(date.timestamp() * 1000)
    bar_interval = util.get_interval(bar)
    # 终止毫秒时间戳
    end_ts = start_ts + 1000 * 3600 * 24

    before_ts = start_ts
    candle_list = []
    lg.info('get symboa: %s, date: %s, start: %s', symbol, date, before_ts)
    while True:
        # 计算limit
        limit = util.get_limit(num=(end_ts - before_ts) / bar_interval + 1)
        # 获取K线数据
        result = spot_client.klines(
            symbol=symbol,
            interval=bar,
            startTime=before_ts - 1,
            endTime=before_ts + (limit - 1) * bar_interval + 1,
            limit=limit,
        )
        # [ERROR RETURN] K线数据错误
        # [BREAK] 数据为空
        if not result:
            lg.error("msg: data not found")
            break
        # 保存candle
        candle_list += result
        # 跳过上一次的endTime，上一次的endTime=before_ts + (limit - 1) * bar_interval
        before_ts = before_ts + limit * bar_interval
        # [BREAK] 完成
        if before_ts > end_ts:
            break
        time.sleep(0.3)
    df = pd.DataFrame(candle_list).astype(float)
    if len(df) == 0:
        return df
    # 按照时间戳去重
    ts_column = df.columns.tolist()[0]
    df[ts_column] = df[ts_column].astype(int)
    df = df.drop_duplicates(subset=ts_column)
    df = df.sort_values(by=ts_column)
    return df


# res = spot_client.exchange_info()
# for produdct in res['symbols']:
#     if produdct['symbol'] == 'BTCUSDT':
#         print(json.dumps(produdct))

# res = um_futures_client.klines(symbol='BTCUSDT_240628', interval='1m', startTime=1704902400000, endTime=1704902460000)
# print(json.dumps(res))

def kline2df(kline):
    header = ['ts', 'o', 'h', 'l', 'c', 'vol', 'ts_c', 'volCcy', 'volCnt', 'vol_zhudong', 'volCcy_zhudong', 'ignore']
    if len(kline) == 0:
        raise ValueError('no data found')
    df = pd.DataFrame(kline).astype(float)
    # 按照时间戳去重
    ts_column = df.columns.tolist()[0]
    df[ts_column] = df[ts_column].astype(int)
    df = df.drop_duplicates(subset=ts_column)
    df = df.sort_values(by=ts_column)
    df.columns = header
    return df


def run(prod_spot):
    lg.info('prods: %s', prod_spot)
    date_fmt = '%Y-%m-%d'
    end_time = datetime.datetime.strptime('2024-02-01', date_fmt)
    start_time = end_time - datetime.timedelta(days=args.day_diff)
    date_diff = (end_time - start_time).days + 1
    lg.info('start_time: %s, end_time: %s, date_diff: %s', start_time, end_time, date_diff)
    # symbols = ['ETH-USDT', 'ETH-USDT-240628']
    
    bar = '1m'
    return_value_counts = []
    # 按照日期下载
    for i in range(date_diff):
        cur_date = end_time - datetime.timedelta(days=i)
        # lg.info('current date: %s', cur_date)
        cur_q_dt, next_q_dt = get_future_delivery_date(cur_date)
        q_dt = cur_q_dt if args.q_type == 'cq' else next_q_dt
        remaining_days = (q_dt - cur_date).days
        # lg.info('q_dt: %s, remaining_days: %s',
        #         q_dt, remaining_days)
        start_ts = int(cur_date.timestamp() * 1000)
        end_ts = start_ts + 1000 * 3600 * 24 - 1    

        f = os.path.join('kline', prod_spot, cur_date.strftime(date_fmt), bar, 'data.csv')
        if os.path.exists(f):
            df_spot = pd.read_csv(f)
        else:
            # 季度交割合约的k线由 已交割合约的k线+当季+下一季拼接而成
            # 最大返回为1000条，1分钟bar有1440条数据所以请求2次
            kline_spot = spot_client.klines(symbol=prod_spot,
                                            interval=bar,
                                            startTime=start_ts,
                                            endTime=start_ts + 1000 * 3600 * 12 - 1,
                                            limit=1000,
                                            )
            kline_spot1 = spot_client.klines(symbol=prod_spot,
                                            interval=bar,
                                            startTime=start_ts + 1000 * 3600 * 12,
                                            endTime=start_ts + 1000 * 3600 * 24 - 1,
                                            limit=1000,
                                            )
            kline_spot.extend(kline_spot1)
            df_spot = kline2df(kline_spot)

            if not os.path.exists(os.path.dirname(f)):
                os.makedirs(os.path.dirname(f), exist_ok=True)
            df_spot.to_csv(f, index=False)
        
        # 币本位
        # BTCUSDT -> BTCUSD_240329
        # prod_future = prod_spot[:-1] + "_" + q_dt.strftime('%y%m%d')
        # futures_client = cm_futures_client
        # U本位
        # BTCUSDT -> BTCUSDT_240329
        prod_future = prod_spot + "_" + q_dt.strftime('%y%m%d')
        futures_client = um_futures_client
        # lg.info('%s, prod_future: %s', args.q_type, prod_future)
        f = os.path.join('kline', prod_future, args.q_type, cur_date.strftime(date_fmt), bar, 'data.csv')
        if os.path.exists(f):
            df_future = pd.read_csv(f)
        else:
            # 季度交割合约的k线由 已交割合约的k线+当季+下一季拼接而成
            # 最大返回为1000条，1分钟bar有1440条数据所以请求2次
            kline_spot = futures_client.klines(symbol=prod_future,
                                            interval=bar,
                                            startTime=start_ts,
                                            endTime=start_ts + 1000 * 3600 * 12 - 1,
                                            limit=1000,
                                            )
            if len(kline_spot) == 0:
                # 合约已无数据
                break
            kline_spot1 = futures_client.klines(symbol=prod_future,
                                            interval=bar,
                                            startTime=start_ts + 1000 * 3600 * 12,
                                            endTime=start_ts + 1000 * 3600 * 24 - 1,
                                            limit=1000,
                                            )
            kline_spot.extend(kline_spot1)
            df_future = kline2df(kline_spot)

            if not os.path.exists(os.path.dirname(f)):
                os.makedirs(os.path.dirname(f), exist_ok=True)
            df_future.to_csv(f, index=False)
            time.sleep(0.05)
        
        df = pd.merge(df_spot, df_future, on='ts', how='inner', suffixes=('_spot', '_future'))
        # print('----df head----')
        df['date'] = cur_date.strftime(date_fmt)
        df['dt'] = df['ts'].map(util.ts2dt)
        df['basis'] = (df['c_future'] - df['c_spot']) / (df['c_spot'] + 1)
        df['remaining_days'] = remaining_days
        df['return_year'] = 100 * df['basis'] * 365 / df['remaining_days']
        df['return_year_int'] = df['return_year'].astype(int)

        vc = df['return_year_int'].value_counts()
        return_value_counts.append(vc)
        if i == 5:
            print('return of year describe')
            print(vc)
    
        if i > 0 and i % 365 == 0:
            lg.info('current date: %s', cur_date)
            return_value_counts = pd.concat(return_value_counts)
            lg.info('----return_value_counts----')
            vc = return_value_counts.reset_index()
            vc.columns = ['return_year_int', 'cnt_of_minutes']

            bins = [-100, 0, 5, 8, 10, 12, 15, 18, 20, 30, 50, 1000]
            vc['bins'] = pd.cut(vc['return_year_int'], bins)
            vc = vc.groupby(by='bins')['cnt_of_minutes'].sum()
            vc = vc.reset_index()
            vc.columns = ['bins', 'cnt_of_minutes']
            total = vc['cnt_of_minutes'].sum()
            vc['rate'] = vc['cnt_of_minutes'] / total
            print(vc)
            vc1 = vc.iloc[4:, :]
            lg.info('10%%以上占比: %s', vc1['rate'].sum())
            return_value_counts = []
    lg.info('current date: %s', cur_date)
    return_value_counts = pd.concat(return_value_counts)
    lg.info('----return_value_counts----')
    vc = return_value_counts.reset_index()
    vc.columns = ['return_year_int', 'cnt_of_minutes']

    bins = [-100, 0, 5, 8, 10, 12, 15, 18, 20, 30, 50, 1000]
    vc['bins'] = pd.cut(vc['return_year_int'], bins)
    vc = vc.groupby(by='bins')['cnt_of_minutes'].sum()
    vc = vc.reset_index()
    vc.columns = ['bins', 'cnt_of_minutes']
    total = vc['cnt_of_minutes'].sum()
    vc['rate'] = vc['cnt_of_minutes'] / total
    print(vc)
    vc1 = vc.iloc[4:, :]
    lg.info('10%%以上占比: %s', vc1['rate'].sum())
    return_value_counts = []
    

def test():
    t = datetime.datetime.strptime('2023-08-17', '%Y-%m-%d')
    lg.info('cur_date: %s, %s', t, t.strftime('%y%m%d'))
    res = get_future_delivery_date(t)
    print(res)
    start_ts = int(t.timestamp() * 1000)
    end_ts = start_ts + 1000 * 3600 * 24 - 1
    kline_future = um_futures_client.klines(symbol='BTCUSDT_230929',
                                            interval='1d',
                                            startTime=start_ts,
                                            endTime=end_ts,
                                            limit=2,
                                            )
    print(kline_future)

    kline = spot_client.klines(
                                    symbol='BTCUSDT',
                                    interval='1d',
                                    startTime=start_ts,
                                    endTime=end_ts,
                                    limit=2,
                                )
    print(kline)
    spot_price = float(kline[0][4])
    future_price = float(kline_future[0][4])
    jc = 100 * (future_price - spot_price) / spot_price
    print('jc: {:.2f}, spot: {:.1f}, future: {:.1f}'.format(jc, spot_price, future_price))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str)
    parser.add_argument("--q_type", type=str)
    parser.add_argument("--day_diff", type=int, default=3)
    args, _ = parser.parse_known_args()
    lg.info(args)
    for prod in args.symbol.split(','):
        run(prod)
    # exchange_info()