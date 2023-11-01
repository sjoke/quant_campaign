# 丽海弘金行情网关接入API
## 简介
本API为丽海弘金行情网关接入API，是为了方便用户快速接入数据服务而提供的一套API，用户可以通过数据SDK快速的获取数据服务的数据。
支持行情订阅、历史数据查询、实时数据查询等功能。具备以下功能：
1.订阅推送实时行情
2.查询证券基础信息
3.查询最近一拍行情快照

## 依赖

- Python 3.10+
- protobuf 3

## 数据SDK使用说明

### 示例代码
参考`demo.py` 和 `quote_impl.py`
在`demo.py` 中初始化API，IP, 端口在执行脚本中作为入参：python3 demo.py ip port
在`quote_impl.py` 中 onLoginAns 接口下提供订阅示例，登录成功后订阅代码即可实现断线重连，重新订阅数据

#### 实时行情订阅/取消订阅
调用`self.api_.sub`订阅成功后，数据处理器(参见下文)会收到行情数据。

订阅可以一次订阅一个标的，也可以一次订阅多个标的。
订阅全市场行情，需要订阅所有标的，订阅所有标的的代码为“FFF...FFF” 32个F。
只能分主题订阅。

调用 `self.api_.unsub` 接口取消订阅

#### 实时行情查询
调用 `self.api_.queryCache` 查询实时行情，数据处理器会收到实时行情数据

#### 债券基础信息查询
调用 `self.api_.querySecureMaster` 查询债券基础信息，数据处理器会收到债券基础信息

#### 推送自定义行情
调用 `self.api_.pubCustomData` 推送自定义行情，可通过`self.api_.sub`订阅或`self.api_.queryCache` 查询

#### 数据处理器
`quote_impl.py`中的 `onMsg` 接口，根据数据类型解析订阅消息、实时行情查询等进行业务处理；

### 数据字典

|  主题   |  TOPIC   | 订阅返回数据类型  | 查询返回数据类型  | 备注  |
|  ----  | ----  | ----  |----  |----  |
| LVT  |  1  | SDSLevel2  | SDSLevel2Ans | 沪深行情快照【股票、国债、期货、期权、指数】 |
|  TRD |  2  | SDSTransaction  | SDSTransactionAns  | 沪深逐笔成交 |
|ORD |  3  | SDSOrder  | SDSOrderAns  | 沪深逐笔委托 |
|ORQ |  4  | SDSOrderQueue  | SDSOrderQueueAns | 沪深委托队列 |
|STK |  7  | SDSStock  | SDSStockAns | 沪深股票 |
|FUT |  8  | SDSFuture  | SDSFutureAns | 期货期权 |
|IDX |  9  | SDSIndex  | SDSIndexAns | 沪深指数 |
|QDJ |  11  | SDSExchQDBJ  | SDSExchQDBJAns | 上海债券确定报价 |
|BOR |  12  | SDSBondOrder | SDSBondOrderAns | 深圳债券逐笔委托 |
|BTR |  13  | SDSBONDTransaction  | SDSBONDTransactionAns | 深圳债券平台逐笔成交 |
|BLN |  18  | SDSBondKline | SDSBondKlineAns | 债券分钟线 |
|BDD  |  19  | SDSDeepData  | SDSDeepDataAns | 全市场最优深度行情 |
|CMS |  100  | MarketDataMakingDepth | MarketDataMakingDepthAns | CFETS 做市市场深度行情 |
|CXS |  101  | MarketDataXbondDepth | MarketDataXbondDepthAns | CFETS 匿名点击深度行情 |
|CXB |  102  | MarketDataXbondBest | MarketDataXbondBestAns | CFETS 匿名点击最优报价 |
|CBB |  103  | MarketDataBrokerBest | MarketDataBrokerBestAns | CFETS 经纪行情最优报价 |
|CBE |  104  | MarketDataBrokerExecute | MarketDataBrokerExecuteAns | CFETS 经纪成交行情 |
|CSS |  105  | MarketDataXSwapDepth | MarketDataXSwapDepthAns | CFETS 利率互换深度行情 |
|CSE |  106  | MarketDataXSwapExcute | MarketDataXSwapExcuteAns | CFETS 利率互换逐笔成交 |
|CMS_RAW |  1000  | CFETSRawData | CFETSRawDataAns | 对应CFETS行情的原始数据 |
|CXS_RAW |  1001  | CFETSRawData | CFETSRawDataAns | 对应CFETS行情的原始数据 |
|CXB_RAW |  1002  | CFETSRawData | CFETSRawDataAns | 对应CFETS行情的原始数据 |
|CBB_RAW |  1003  | CFETSRawData | CFETSRawDataAns | 对应CFETS行情的原始数据 |
|CBE_RAW |  1004  | CFETSRawData | CFETSRawDataAns | 对应CFETS行情的原始数据 |
|CSS_RAW |  1005  | CFETSRawData | CFETSRawDataAns | 对应CFETS行情的原始数据 |
|CSE_RAW |  1006  | CFETSRawData | CFETSRawDataAns | 对应CFETS行情的原始数据 |
|SDSCustomData |  20000+(自定义的topic是20000以上任何int)  | SDSCustomData | SDSCustomDataAns/SDSCustomDataPubAns | 自定义行情数据 |

* 具体的消息含义参考proto目录下的 .proto 文件


## 修改记录

20230908 优化断线重连方案
20230911 修复心跳
20230914 捕获断线发送数据异常