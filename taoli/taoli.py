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
import schedule
from typing import Sequence
import argparse


spot_client = Spot()
um_futures_client = UMFutures()
cm_futures_client = CMFutures()
spot_client.ping()
um_futures_client.ping()


def cm_exchange_info():
    res = cm_futures_client.exchange_info()
    # with open('futures_cm_all.json', 'w') as fp:
    #     json.dump(res, fp)
    delivery_prods = [s for s in res['symbols'] if s['contractType'] in ['CURRENT_QUARTER', 'NEXT_QUARTER']]
    # with open('futures_delivery_cm.json', 'w') as fp:
    #     json.dump(delivery_prods, fp)
    return delivery_prods


def um_exchange_info():
    res = um_futures_client.exchange_info()
    # with open('futures_cm_all.json', 'w') as fp:
    #     json.dump(res, fp)
    delivery_prods = [s for s in res['symbols'] if s['contractType'] in ['CURRENT_QUARTER', 'NEXT_QUARTER']]
    # with open('futures_delivery_cm.json', 'w') as fp:
    #     json.dump(delivery_prods, fp)
    return delivery_prods


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


def log_depth(date: datetime.datetime, depths):
    f = os.path.join('depths', date.strftime('%Y-%m-%d'))
    if not os.path.exists(f):
        os.makedirs(f)
    f = os.path.join(f, 'data.csv')
    with open(f, 'a', encoding='utf8') as fp:
        js = json.dumps(depths)
        line = date.strftime('%Y-%m-%d %H:%M:%S') + '\t' + js + '\n'
        fp.write(line)


def calc_jc(prod_future, future_client: Union[CMFutures, UMFutures]):
    symbol = prod_future['symbol']
    lg.debug('future symbol: %s', symbol)
    cur_date = datetime.datetime.now()
    delivery_date = datetime.datetime.fromtimestamp(int(prod_future['deliveryDate'])/1000)
    date_diff = (delivery_date - cur_date).days
    lg.debug('cur_date: %s, delivery_date: %s, date_diff: %s', cur_date, delivery_date, date_diff)
    
    prod_spot = prod_future['baseAsset'] + 'USDT'
    depth_pos = args.depth_pos
    depths = spot_client.depth(prod_spot, limit=50)
    spot_price_buy = float(depths['asks'][depth_pos][0])
    spot_amt_buy = float(depths['asks'][depth_pos][1])
    log_depth(cur_date, depths)

    depths = future_client.depth(symbol, limit=50)
    future_price_sell = float(depths['bids'][depth_pos][0])
    future_amt_sell = float(depths['bids'][depth_pos][1])
    log_depth(cur_date, depths)

    basis = 100 * (future_price_sell - spot_price_buy) / spot_price_buy
    jc = basis * 365 / date_diff
    return [symbol, basis, jc,  spot_price_buy, future_price_sell, date_diff]


def trade(prod_jc, prod_future, future_client: Union[CMFutures, UMFutures]):
    future_symbol = prod_jc[0]
    base_asset = prod_future['baseAsset']
    spot_symbol = base_asset + 'USDT'
    spot_price_buy, future_price_sell = prod_jc[3], prod_jc[4]
    balance_usdt = 0
    for balance in spot_client.balance():
        # // 可用下单余额
        if balance['asset'] == 'USDT':
            balance_usdt = balance['availableBalance']
            break
    if balance_usdt <= 10:
        return
    
    # "OrderType": [ // 订单类型
    #     "LIMIT",  // 限价单
    #     "MARKET",  // 市价单
    #     "STOP", // 止损单
    #     "TAKE_PROFIT", // 止盈单
    #     "TRAILING_STOP_MARKET" // 跟踪止损单
    # ],
    # "timeInForce": [ // 有效方式
    #     "GTC", // 成交为止, 一直有效
    #     "IOC", // 无法立即成交(吃单)的部分就撤销
    #     "FOK", // 无法全部立即成交就撤销
    #     "GTX" // 无法成为挂单方就撤销
    # ],
    # 1.现货多单
    resp = spot_client.new_order_test(spot_symbol, 'BUY', 'LIMIT', price=spot_price_buy, quantity=1, timeInForce='FOK')
    if resp and resp['orderId']:
        lg.info("现货[%s]成功下单: %s", spot_symbol, json.dumps(resp))
    else:
        lg.warning("现货[%s]下单不成功", spot_symbol)
        return
    
    # 2.现货资产转移到币本位合约
    cumBase = float(resp['cumBase'])
    spot_client.futures_transfer(base_asset, cumBase, 3)
    if resp and resp['tranId']:
        lg.info('现货 to 币本位合约账户成功: %s, %s', base_asset, resp['cumBase'])
    else:
        lg.error('现货 to 币本位合约账户不成功: %s, %s', base_asset, resp['cumBase'])
        return
    
    # 3.合约下一个空单
    resp = future_client.new_order_test(future_symbol, 'SELL', 'LIMIT', price=future_price_sell, quantity=1, timeInForce='FOK')
    if resp and resp['orderId']:
        lg.info("合约[%s]成功下单: %s", future_symbol, json.dumps(resp))
    else:
        lg.error("合约[%s]下单不成功", future_symbol)
        # todo: 现货退单
        # 3.2 币本位合约->现货账户
        spot_client.futures_transfer(base_asset, cumBase, 4)
        # 3.3立即出售，不考虑手续费等损失
        depths = spot_client.depth(spot_symbol, limit=20)
        price = float(depths['bids'][5][0])
        spot_client.new_order_test(spot_symbol, 'SELL', 'LIMIT', price=price, quantity=1, timeInForce='FOK')
        lg.info('成功撤销现货单!')
        return


def run():
    global last_time_wx_send
    lg.info('------------------------')
    now = datetime.datetime.now()
    prods = []
    exchanges = [(cm_exchange_info(), cm_futures_client), (um_exchange_info(), um_futures_client)]
    for prod_futures, future_client in exchanges:
        for prod_future in prod_futures:
            prod_jc = calc_jc(prod_future, future_client)
            # if prod_jc[2] >= args.return_rate:
            #     trade(prod_jc, prod_future, future_client)
            prods.append(prod_jc)

    prods.sort(key=lambda x: x[2], reverse=True)
    msgs = []
    for p in prods:
        # [symbol, basis, jc,  spot_price_buy, future_price_sell, date_diff]
        s = "{}, 收益: {:.2f}%, 年化{:.2f}%, spot: {}, future: {}, remain_days: {}".format(
            p[0],p[1],p[2],p[3],p[4],p[5]
        )
        lg.info(s)
        # 收益率超过阈值或者utc+8上午9点, 发，只发前5条
        if (p[2] >= args.return_rate or now.utcnow().hour == 1) and len(msgs) < 5:
            s = now.strftime('%Y%m%d-%H%M%S') + ': ' + s
            msgs.append(s)
    # 如果有消息且离上次发送时间超过0.5小时，则再次发送
    if len(msgs) > 0 and (last_time_wx_send is None or (now - last_time_wx_send).seconds >= 60 * 30):
        s = '\n'.join(msgs)
        lg.info('----wx send----\n%s', s)
        last_time_wx_send = now
        util.wx_send(s)


def main():
    run()
    if args.every_n_seconds > 0:
        schedule.every(args.every_n_seconds).seconds.do(run)
        while True:
            schedule.run_pending()
            time.sleep(0.001)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--return_rate", type=float, default=15)
    parser.add_argument("--every_n_seconds", type=int, default=0)
    parser.add_argument("--depth_pos", type=int, default=10)
    parser.add_argument("--is_lixing", action='store_true')
    args, _ = parser.parse_known_args()
    if args.is_lixing:
        lg = util.get_logger(with_console=False, with_file=True)
    else:
        lg = util.get_logger()
    lg.info(args)

    last_time_wx_send = None
    main()
