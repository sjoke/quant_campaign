import time
from tqdm import tqdm
import datetime
import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.subAccount_api as SubAccount
import okex.status_api as Status
import json
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

def run():
    lg.info('task run!')
    result = publicAPI.get_instruments(instType="FUTURES")
    today = datetime.datetime.today()
    now = datetime.datetime.now()
    products = []
    # for future in tqdm(result['data'], total=len(result['data'])):
    for future in result['data']:
        instId = future['instId']
        instFamily = future['instFamily']
        if future['alias'] not in ['quarter', 'next_quarter']:
            continue
        # print('------')
        # print('instId: ', instId, ', instFamily: ', instFamily, ', alias: ', future['alias'])
        # spot_ticker = marketAPI.get_ticker(instFamily)
        # 保守计算，以卖方第20档深度价格买入
        spot_instid = instId.split('-')[0] + '-USDT'
        spot_ticker = marketAPI.get_orderbook(spot_instid, 20)
        if len(spot_ticker['data']) == 0:
            lg.warn('no spot ticker, %s', spot_instid)
            continue
        spot_price_buy = float(spot_ticker['data'][0]['asks'][-1][0])
        spot_price_sell = float(spot_ticker['data'][0]['bids'][-1][0])
        # print('spot_price: ', spot_price)

        # futures = publicAPI.get_instruments(instType='FUTURES', uly=instId)
        # future_q = [f for f in futures['data'] if f['alias'] == 'quarter']
        # if len(future_q) == 0:
        #     continue
        # future_q = future_q[0]
        # print(future_q)
        expire_dt = datetime.datetime.fromtimestamp(int(future['expTime'])/1000)
        # future_ticker = marketAPI.get_ticker(instId)
        future_ticker = marketAPI.get_orderbook(instId, 20)
        if future_ticker['data'] == 0:
            lg.warn('no future ticker: %s', instId)
            continue
        future_price_sell = float(future_ticker['data'][0]['bids'][-1][0])
        future_price_buy = float(future_ticker['data'][0]['asks'][-1][0])
        # print('future_price: ', future_price)

        date_diff = (expire_dt - today).days
        expire_day = expire_dt.strftime('%Y%m%d')
        # print('{} spot_price: {}, future_price: {}, days: {}'.format(instId, spot_price, future_price, date_diff))
        basis = 100 * (future_price_sell - spot_price_buy) / spot_price_buy
        jc = basis * 365 / date_diff
        # print('{} cq jicha: {:.4f}'.format(instId, jc))
        products.append([instId, basis, jc,  spot_price_buy, future_price_sell, expire_day, date_diff, 'spot_buy'])
        # basis = 100 * (spot_price_sell - future_price_buy) / future_price_buy
        # jc = basis * 365 / date_diff
        # # print('{} cq jicha: {:.4f}'.format(instId, jc))
        # products.append([instId, basis, jc,  spot_price_sell, future_price_buy, expire_day, date_diff, 'spot_sell'])
        # break
        # time.sleep(0.01)
    products.sort(key=lambda x: x[2], reverse=True)

    msgs = []
    for p in products:
        s = "{}, 收益: {:.2f}%, 年化{:.2f}%, spot: {}, future: {}, remain_days: {}, op: {}".format(
            p[0],p[1],p[2],p[3],p[4],p[6],p[7]
        )
        lg.info(s)
        # utc+8 上午9点发一条
        if (p[2] >= args.return_rate or now.utcnow().hour == 1) and len(msgs) <= 5:
            s = now.strftime('%Y%m%d-%H%M%S') + ': ' + s
            msgs.append(s)
    if len(msgs) > 0:
        s = '\n'.join(msgs)
        lg.info('----wx send----')
        lg.info(s)
        util.wx_send(s)
    # print(json.dumps(result))


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

    # account api
    accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
    # 查看账户持仓风险 GET Position_risk
    # result = accountAPI.get_position_risk('SWAP')
    # 查看账户余额  Get Balance
    # result = accountAPI.get_account()
    # 查看持仓信息  Get Positions
    # result = accountAPI.get_positions('FUTURES', 'BTC-USD-210402')
    # 账单流水查询（近七天） Get Bills Details (recent 7 days)
    # result = accountAPI.get_bills_detail('FUTURES', 'BTC','cross')
    # 账单流水查询（近三个月） Get Bills Details (recent 3 months)
    # result = accountAPI.get_bills_details('FUTURES', 'BTC','cross')
    # 查看账户配置  Get Account Configuration
    # result = accountAPI.get_account_config()
    # 设置持仓模式  Set Position mode
    # result = accountAPI.get_position_mode('long_short_mode')
    # 设置杠杆倍数  Set Leverage
    # result = accountAPI.set_leverage(instId='BTC-USD-210402', lever='10', mgnMode='cross')
    # 获取最大可交易数量  Get Maximum Tradable Size For Instrument
    # result = accountAPI.get_maximum_trade_size('BTC-USDT-210402', 'cross', 'USDT')
    # 获取最大可用数量  Get Maximum Available Tradable Amount
    # result = accountAPI.get_max_avail_size('BTC-USDT-210402', 'isolated', 'BTC')
    # 调整保证金  Increase/Decrease margint
    # result = accountAPI.Adjustment_margin('BTC-USDT-210409', 'long', 'add', '100')
    # 获取杠杆倍数 Get Leverage
    # result = accountAPI.get_leverage('BTC-USDT-210409', 'isolated')
    # 获取币币逐仓杠杆最大可借  Get the maximum loan of isolated MARGIN
    # result = accountAPI.get_max_load('BTC-USDT', 'cross', 'BTC')
    # 获取当前账户交易手续费费率  Get Fee Rates
    # result = accountAPI.get_fee_rates('FUTURES', '', category='1')
    # 获取计息记录  Get interest-accrued
    # result = accountAPI.get_interest_accrued('BTC-USDT', 'BTC', 'isolated', '', '', '10')
    # 获取用户当前杠杆借币利率 Get Interest-accrued
    # result = accountAPI.get_interest_rate()
    # 期权希腊字母PA / BS切换  Set Greeks (PA/BS)
    # result = accountAPI.set_greeks('BS')
    # 查看账户最大可转余额  Get Maximum Withdrawals
    # result = accountAPI.get_max_withdrawal('')

    # funding api
    fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
    # 获取充值地址信息  Get Deposit Address
    # result = fundingAPI.get_deposit_address('')
    # 获取资金账户余额信息  Get Balance
    # result = fundingAPI.get_balances('BTC')
    # 资金划转  Funds Transfer
    # result = fundingAPI.funds_transfer(ccy='', amt='', type='1', froms="", to="",subAcct='')
    # 提币  Withdrawal
    # result = fundingAPI.coin_withdraw('usdt', '2', '3', '', '', '0')
    # 充值记录  Get Deposit History
    # result = fundingAPI.get_deposit_history()
    # 提币记录  Get Withdrawal History
    # result = fundingAPI.get_withdrawal_history()
    # 获取币种列表  Get Currencies
    # result = fundingAPI.get_currency()
    # 余币宝申购/赎回  PiggyBank Purchase/Redemption
    # result = fundingAPI.purchase_redempt('BTC', '1', 'purchase')
    # 资金流水查询  Asset Bills Details
    # result = fundingAPI.get_bills()

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
    # result = marketAPI.get_history_candlesticks('BTC-USDT')
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

    # public api
    publicAPI = Public.PublicAPI(api_key, secret_key, passphrase, False, flag)
    # 获取交易产品基础信息  Get instrument
    # result = publicAPI.get_instruments('FUTURES', 'BTC-USDT')
    # 获取交割和行权记录  Get Delivery/Exercise History
    # result = publicAPI.get_deliver_history('FUTURES', 'BTC-USD')
    # 获取持仓总量  Get Open Interest
    # result = publicAPI.get_open_interest('SWAP')
    # 获取永续合约当前资金费率  Get Funding Rate
    # result = publicAPI.get_funding_rate('BTC-USD-SWAP')
    # 获取永续合约历史资金费率  Get Funding Rate History
    # result = publicAPI.funding_rate_history('BTC-USD-SWAP')
    # 获取限价  Get Limit Price
    # result = publicAPI.get_price_limit('BTC-USD-210402')
    # 获取期权定价  Get Option Market Data
    # result = publicAPI.get_opt_summary('BTC-USD')
    # 获取预估交割/行权价格  Get Estimated Delivery/Excercise Price
    # result = publicAPI.get_estimated_price('ETH-USD-210326')
    # 获取免息额度和币种折算率  Get Discount Rate And Interest-Free Quota
    # result = publicAPI.discount_interest_free_quota('')
    # 获取系统时间  Get System Time
    # result = publicAPI.get_system_time()
    # 获取平台公共爆仓单信息  Get Liquidation Orders
    # result = publicAPI.get_liquidation_orders('FUTURES', uly='BTC-USDT', alias='next_quarter', state='filled')
    # 获取标记价格  Get Mark Price
    # result = publicAPI.get_mark_price('FUTURES')
    # 获取合约衍生品仓位档位 Get Tier
    # result = publicAPI.get_tier(instType='MARGIN', instId='BTC-USDT', tdMode='cross')

    # trade api
    tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
    # 下单  Place Order
    # result = tradeAPI.place_order(instId='BTC-USDT-210326', tdMode='cross', side='sell', posSide='short',
    #                               ordType='market', sz='100')
    # 批量下单  Place Multiple Orders
    # result = tradeAPI.place_multiple_orders([
    #     {'instId': 'BTC-USD-210402', 'tdMode': 'isolated', 'side': 'buy', 'ordType': 'limit', 'sz': '1', 'px': '17400',
    #      'posSide': 'long',
    #      'clOrdId': 'a12344', 'tag': 'test1210'},
    #     {'instId': 'BTC-USD-210409', 'tdMode': 'isolated', 'side': 'buy', 'ordType': 'limit', 'sz': '1', 'px': '17359',
    #      'posSide': 'long',
    #      'clOrdId': 'a12344444', 'tag': 'test1211'}
    # ])

    # 撤单  Cancel Order
    # result = tradeAPI.cancel_order('BTC-USD-201225', '257164323454332928')
    # 批量撤单  Cancel Multiple Orders
    # result = tradeAPI.cancel_multiple_orders([
    #     {"instId": "BTC-USD-210402", "ordId": "297389358169071616"},
    #     {"instId": "BTC-USD-210409", "ordId": "297389358169071617"}
    # ])

    # 修改订单  Amend Order
    # result = tradeAPI.amend_order()
    # 批量修改订单  Amend Multiple Orders
    # result = tradeAPI.amend_multiple_orders(
    #     [{'instId': 'BTC-USD-201225', 'cxlOnFail': 'false', 'ordId': '257551616434384896', 'newPx': '17880'},
    #      {'instId': 'BTC-USD-201225', 'cxlOnFail': 'false', 'ordId': '257551616652488704', 'newPx': '17882'}
    #      ])

    # 市价仓位全平  Close Positions
    # result = tradeAPI.close_positions('BTC-USDT-210409', 'isolated', 'long', '')
    # 获取订单信息  Get Order Details
    # result = tradeAPI.get_orders('BTC-USD-201225', '257173039968825345')
    # 获取未成交订单列表  Get Order List
    # result = tradeAPI.get_order_list()
    # 获取历史订单记录（近七天） Get Order History (last 7 days）
    # result = tradeAPI.get_orders_history('FUTURES')
    # 获取历史订单记录（近三个月） Get Order History (last 3 months)
    # result = tradeAPI.orders_history_archive('FUTURES')
    # 获取成交明细  Get Transaction Details
    # result = tradeAPI.get_fills()
    # 策略委托下单  Place Algo Order
    # result = tradeAPI.place_algo_order('BTC-USDT-210409', 'isolated', 'buy', ordType='conditional',
    #                                    sz='100',posSide='long', tpTriggerPx='60000', tpOrdPx='59999')
    # 撤销策略委托订单  Cancel Algo Order
    # result = tradeAPI.cancel_algo_order([{'algoId': '297394002194735104', 'instId': 'BTC-USDT-210409'}])
    # 获取未完成策略委托单列表  Get Algo Order List
    # result = tradeAPI.order_algos_list('conditional', instType='FUTURES')
    # 获取历史策略委托单列表  Get Algo Order History
    # result = tradeAPI.order_algos_history('conditional', 'canceled', instType='FUTURES')

    # 子账户API subAccount
    subAccountAPI = SubAccount.SubAccountAPI(api_key, secret_key, passphrase, False, flag)
    # 查询子账户的交易账户余额(适用于母账户) Query detailed balance info of Trading Account of a sub-account via the master account
    # result = subAccountAPI.balances(subAcct='')
    # 查询子账户转账记录(仅适用于母账户) History of sub-account transfer(applies to master accounts only)
    # result = subAccountAPI.bills()
    # 删除子账户APIKey(仅适用于母账户) Delete the APIkey of sub-accounts (applies to master accounts only)
    # result = subAccountAPI.delete(pwd='', subAcct='', apiKey='')
    # 重置子账户的APIKey(仅适用于母账户) Reset the APIkey of a sub-account(applies to master accounts only)
    # result = subAccountAPI.reset(pwd='', subAcct='', label='', apiKey='', perm='')
    # 创建子账户的APIKey(仅适用于母账户) Create an APIkey for a sub-account(applies to master accounts only)
    # result = subAccountAPI.create(pwd='123456', subAcct='', label='', Passphrase='')
    # 查看子账户列表(仅适用于母账户) View sub-account list(applies to master accounts only)
    # result = subAccountAPI.view_list()
    # 母账户控制子账户与子账户之间划转（仅适用于母账户）manage the transfers between sub-accounts(applies to master accounts only)
    # result = subAccountAPI.control_transfer(ccy='', amt='', froms='', to='', fromSubAccount='', toSubAccount='')

    # 系统状态API(仅适用于实盘) system status
    Status = Status.StatusAPI(api_key, secret_key, passphrase, False, flag)
    # 查看系统的升级状态
    # result = Status.status()
    # print(json.dumps(result))
    main()
