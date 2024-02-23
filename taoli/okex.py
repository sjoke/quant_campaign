import json
import okx.MarketData as MarketData
import okx.PublicData as PublicData


if __name__ == '__main__':
    api_key = "fefdb6ca-18ae-4837-a481-398cafe2b5d0"
    secret_key = "06C47E341C8BCFCA844B76B38709AE08"
    passphrase = "HelloWorld123!"
    # flag是实盘与模拟盘的切换参数 flag is the key parameter which can help you to change between demo and real trading.
    flag = '1'  # 模拟盘 demo trading
    # flag = '0'  # 实盘 real trading
    public_api = PublicData.PublicAPI(api_key, secret_key, passphrase)
    result = public_api.get_instruments(instType='FUTURES', uly='BTC-USDT')
    print(json.dumps(result))

    # httpx.ConnectTimeout: timed out
