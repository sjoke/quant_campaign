
import time
import os
import pandas as pd
from tqdm import tqdm
import datetime
from typing import Literal, Union
import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.subAccount_api as SubAccount
import okex.status_api as Status
import json
import paux
import argparse
import logging as lg
import util
import schedule

lg.basicConfig(level=lg.INFO,
               format='%(asctime)s.%(msecs)03d %(levelname)s ' +
               '%(filename)s:%(lineno)d: %(message)s',
               datefmt='%Y-%m-%d %H:%M:%S',
            #    filename='./logs/{}.log'.format(datetime.date.today().strftime('%Y%m%d'))
               )

TIMEZONE = 'Asia/Shanghai'


def is_month_end(date: datetime.datetime):
    t = date + datetime.timedelta(days=7)
    return date.month != t.month


def get_future_delivery_date(date: datetime.datetime) -> list[datetime.datetime]:
    # 季度合约，每个自然季度月的最后一个星期五，08:00:00 UTC
    # 交割价格：交割前最后1小时，每秒现货价格的平均值
    # okex: 当周/次周，当月/次月,当季/次季
    delivery_dates = [None] * 6
    for i in range(1, 10):
        day = date + datetime.timedelta(days=i)
        # 当周周五
        if day.weekday() == 4:
            delivery_dates[0] = day
            break
    # 次周周五
    delivery_dates[1] = delivery_dates[0] + datetime.timedelta(days=7)

    # 当月
    for i in range(7, 100, 7):
        day = delivery_dates[1] + datetime.timedelta(days=i)
        # 月末周五
        if is_month_end(day):
            delivery_dates[2] = day
            break
    # 次月
    for i in range(7, 100, 7):
        day = delivery_dates[2] + datetime.timedelta(days=i)
        # 月末周五
        if is_month_end(day):
            delivery_dates[3] = day
            break
    
    # 当季
    for i in range(7, 100, 7):
        day = delivery_dates[3] + datetime.timedelta(days=i)
        # 月末周五
        if is_month_end(day) and day.month in [3, 6, 9, 12]:
            delivery_dates[4] = day
            break
    # 次季
    for i in range(7, 100, 7):
        day = delivery_dates[4] + datetime.timedelta(days=i)
        # 月末周五
        if is_month_end(day) and day.month in [3, 6, 9, 12]:
            delivery_dates[5] = day
            break
    return delivery_dates


def download_candles_by_dates(
        symbols,
        start: Union[str, int, float, datetime.date],
        end: Union[str, int, float, datetime.date, None] = None,
        bar: str = '1H',
        replace=False,
    ):
    '''
    :param start: 起始日期
    :param end: 终止日期
        None 使用昨日日期
    :param replace: 是否替换本地文件
    '''
    # 执行下载使用的临时过滤器，过滤数据异常的产品
    # 日期终点
    # 需要下载的日期序列
    date_range = paux.date.get_range_dates(start=start, end=end, timezone=TIMEZONE)
    # 反转日期序列，用于加速
    date_range = sorted(date_range, reverse=True)
    print('date_range: ', date_range)
    # 按照日期下载
    for date in date_range:
        for symbol in symbols:
            df = download_candles_by_date(
                symbol=symbol,
                date=date,
                bar=bar,
                replace=replace,
            )


# 下载某一天多产品历史K线数据
def download_candles_by_date(
        symbol,
        date: Union[str, int, float, datetime.date],
        bar,
    ):
    global MarketAPI
    '''
    :param date: 日期
    :param replace: 是否替换本地文件
    '''
    # 日期时间对象，其中小时分钟秒均为0
    date = paux.date.to_datetime(date=date, timezone=TIMEZONE)
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
        result = marketAPI.get_history_candlesticks(
            instId=symbol,
            before=before_ts - 1,
            after=before_ts + (limit - 1) * bar_interval + 1,
            bar=bar,
            limit=limit,
        )
        # [ERROR RETURN] K线数据错误
        if result['code'] != '0':
            lg.error("code: %s, msg: %s", result['code'], result['msg'])
            break
        # [BREAK] 数据为空
        if not result['data']:
            lg.error("msg: data not found")
            break
        # 保存candle
        candle_list += result['data']
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


def run():
    lg.info('task run!')
    start = '2023-01-01'
    end = '2024-02-01'
    start_ts = util.dt2ts(start, fmt='%Y-%m-%d')
    end_ts = util.dt2ts(end, fmt='%Y-%m-%d')
    symbols = ['ETH-USDT', 'ETH-USDT-240628']
    # symbols = ['BTC-USDT', 'BTC-USDT-240927']
    date_range = paux.date.get_range_dates(start=start, end=end, timezone=TIMEZONE)
    # 反转日期序列，用于加速
    date_range = sorted(date_range, reverse=True)
    print('date_range: ', date_range)
    
    bar = '1m'
    flag_data = True
    header = ['ts', 'o', 'h', 'l', 'c', 'vol', 'volCcy', 'volCcyQuote', 'confirm']
    # 按照日期下载
    for date in date_range:
        if not flag_data:
            break
        lg.info('current date: %s', date)
        dt = paux.date.to_datetime(date=date, timezone=TIMEZONE)
        next_q_dt = get_future_delivery_date(dt)[-1].date()
        remaining_days = (next_q_dt - dt).days
        lg.info('next_q_dt: %s, remaining_days: %s', next_q_dt, remaining_days)
        
        df_spot = pd.DataFrame()
        df_future = pd.DataFrame()
        for symbol in symbols:
            df = download_candles_by_date(
                symbol=symbol,
                date=date,
                bar=bar,
            )
            # print(df.head())
            if len(df) == 0:
                lg.error('inst: %s, date: %s, no data found!', symbol, date)
                util.wx_send('inst: %s, date: %s, no data found!' % (symbol, date))
                flag_data = False
                break
            df.columns = header
            if len(symbol.split('-')) == 2:
                df_spot = df
            else:
                df_future = df
            f = os.path.join('candles', symbol, date, bar, 'data.csv')
            if not os.path.exists(os.path.dirname(f)):
                os.makedirs(os.path.dirname(f), exist_ok=True)
            df.to_csv(f, index=False)
        
        if len(df_spot) > 0 and len(df_future) > 0:
            df1 = pd.merge(df_spot, df_future, on='ts', how='inner', suffixes=('_spot', '_future'))
            # print('----df head----')
            # print(df1.head())
            df1['basis'] = (df1['c_future'] - df1['c_spot']) / (df1['c_spot'] + 1)
            df1['remaining_days'] = remaining_days
            df1['return_year'] = 100 * df1['basis'] * 365 / df1['remaining_days']
            df1['return_year_int'] = df1['return_year'].astype(int)
            # print('return of year describe')
            print(df1['return_year_int'].value_counts())
            f = os.path.join('candles', 'ETH-DIFF', date, bar, 'data.csv')
            if not os.path.exists(os.path.dirname(f)):
                os.makedirs(os.path.dirname(f), exist_ok=True)
            df1.to_csv(f, index=False)
        # break
            




    # result = marketAPI.get_history_candlesticks('BTC-USDT-240628', 
    #                                             after=start_ts, 
    #                                             before=end_ts,
    #                                             bar='1H', 
    #                                             limit=100)
    # print(result)
    # for r in result['data']:
    #     r.append(util.ts2dt(r[0]))
    #     print(r)
        
    


def main():
    run()
    if args.every_n_minute > 0:
        schedule.every(args.every_n_minute).minutes.do(run)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    # nohup python -u taoli.py --return_rate 20 --every_n_minute 60 >logs/20240122.log 2>&1 &
    api_key = "fefdb6ca-18ae-4837-a481-398cafe2b5d0"
    secret_key = "06C47E341C8BCFCA844B76B38709AE08"
    passphrase = "HelloWorld123!"

    parser = argparse.ArgumentParser()
    parser.add_argument("--return_rate", type=float, default=15)
    parser.add_argument("--every_n_minute", type=int, default=0)
    args = parser.parse_args()
    lg.info("args: %s", args)
    # flag是实盘与模拟盘的切换参数 flag is the key parameter which can help you to change between demo and real trading.
    # flag = '1'  # 模拟盘 demo trading
    flag = '0'  # 实盘 real trading

    # market api
    marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)
    # 获取所有产品行情信息  Get Tickers
    # result = marketAPI.get_tickers('SPOT')
    # 获取单个产品行情信息  Get Ticker
    # result = marketAPI.get_ticker('BTC-USDT')
    # 获取指数行情  Get Index Tickers
    # result = marketAPI.get_index_ticker('BTC', 'BTC-USD')
    # 获取产品深度  Get Order Book
    # result = marketAPI.get_orderbook('BTC-USDT-210402', '400')
    # 获取所有交易产品K线数据  Get Candlesticks
    # result = marketAPI.get_candlesticks('BTC-USDT-210924', bar='1m')
    # 获取交易产品历史K线数据（仅主流币实盘数据）  Get Candlesticks History（top currencies in real-trading only）
    result = marketAPI.get_history_candlesticks('BTC-USDT', bar='1m')
    # 获取指数K线数据  Get Index Candlesticks
    # result = marketAPI.get_index_candlesticks('BTC-USDT')
    # 获取标记价格K线数据  Get Mark Price Candlesticks
    # result = marketAPI.get_markprice_candlesticks('BTC-USDT')
    # 获取交易产品公共成交数据  Get Trades
    # result = marketAPI.get_trades('BTC-USDT', '400')
    # 获取平台24小时成交总量  Get Platform 24 Volume
    # result = marketAPI.get_volume()
    # Oracle 上链交易数据 GET Oracle
    # result = marketAPI.get_oracle()

    # 系统状态API(仅适用于实盘) system status
    Status = Status.StatusAPI(api_key, secret_key, passphrase, False, flag)
    # 查看系统的升级状态
    # result = Status.status()
    # print(json.dumps(result))
    main()
