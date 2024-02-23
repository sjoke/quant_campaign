from taoli import trade, cm_futures_client
import numpy as np
import pandas as pd
import datetime



def test_trade():
    prod_jc = ['BTCUSD_240329', 1.5251243713374112, 12.101530337785979, 48120.01, 48853.9, 46]
    prod_future = {'symbol': 'BTCUSD_240329', 'pair': 'BTCUSD', 'contractType': 'CURRENT_QUARTER', 'deliveryDate': 1711699200000, 'onboardDate': 1695974400000, 'contractStatus': 'TRADING', 'contractSize': 100, 'marginAsset': 'BTC', 'maintMarginPercent': '2.5000', 'requiredMarginPercent': '5.0000', 'baseAsset': 'BTC', 'quoteAsset': 'USD', 'pricePrecision': 1, 'quantityPrecision': 0, 'baseAssetPrecision': 8, 'quotePrecision': 8, 'equalQtyPrecision': 4, 'maxMoveOrderLimit': 10000, 'triggerProtect': '0.0500', 'underlyingType': 'COIN', 'underlyingSubType': [], 'filters': [{'minPrice': '1000', 'maxPrice': '4671848', 'filterType': 'PRICE_FILTER', 'tickSize': '0.1'}, {'stepSize': '1', 'filterType': 'LOT_SIZE', 'maxQty': '1000000', 'minQty': '1'}, {'stepSize': '1', 'filterType': 'MARKET_LOT_SIZE', 'maxQty': '1000', 'minQty': '1'}, {'limit': 200, 'filterType': 'MAX_NUM_ORDERS'}, {'limit': 20, 'filterType': 'MAX_NUM_ALGO_ORDERS'}, {'multiplierDown': '0.9500', 'multiplierUp': '1.0500', 'multiplierDecimal': '4', 'filterType': 'PERCENT_PRICE'}], 'orderTypes': ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET'], 'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX'], 'liquidationFee': '0.010000', 'marketTakeBound': '0.05'}
    trade(prod_jc, prod_future, cm_futures_client)