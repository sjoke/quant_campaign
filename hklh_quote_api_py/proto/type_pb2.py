# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: type.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ntype.proto\x12\x0ehklh_quote_api*\xe8\x02\n\x0bSDSDataType\x12\r\n\tTypeBegin\x10\x00\x12\x07\n\x03LVT\x10\x01\x12\x07\n\x03TRD\x10\x02\x12\x07\n\x03ORD\x10\x03\x12\x07\n\x03ORQ\x10\x04\x12\x07\n\x03KLN\x10\x05\x12\x07\n\x03MNT\x10\x06\x12\x07\n\x03STK\x10\x07\x12\x07\n\x03\x46UT\x10\x08\x12\x07\n\x03IDX\x10\t\x12\x07\n\x03\x45\x42\x44\x10\n\x12\x07\n\x03QDJ\x10\x0b\x12\x07\n\x03\x42OR\x10\x0c\x12\x07\n\x03\x42TR\x10\r\x12\x07\n\x03\x44MD\x10\x0e\x12\x07\n\x03\x42\x42Q\x10\x0f\x12\x07\n\x03SDB\x10\x10\x12\x07\n\x03\x42\x44\x46\x10\x11\x12\x07\n\x03\x42LN\x10\x12\x12\x07\n\x03\x42\x44\x44\x10\x13\x12\x07\n\x03\x43MS\x10\x64\x12\x07\n\x03\x43XS\x10\x65\x12\x07\n\x03\x43XB\x10\x66\x12\x07\n\x03\x43\x42\x42\x10g\x12\x07\n\x03\x43\x42\x45\x10h\x12\x07\n\x03\x43SS\x10i\x12\x07\n\x03\x43SE\x10j\x12\x0c\n\x07\x43MS_RAW\x10\xe8\x07\x12\x0c\n\x07\x43XS_RAW\x10\xe9\x07\x12\x0c\n\x07\x43XB_RAW\x10\xea\x07\x12\x0c\n\x07\x43\x42\x42_RAW\x10\xeb\x07\x12\x0c\n\x07\x43\x42\x45_RAW\x10\xec\x07\x12\x0c\n\x07\x43SS_RAW\x10\xed\x07\x12\x0c\n\x07\x43SE_RAW\x10\xee\x07*\x81\x05\n\nSDSMsgType\x12\x13\n\x0fkMtMsgTypeBegin\x10\x00\x12\x10\n\x0ckMtHeartBeat\x10\x65\x12\x13\n\x0fkMtHeartBeatAns\x10\x66\x12\x12\n\x0ekMtLoginMegate\x10g\x12\x15\n\x11kMtLoginMegateAns\x10h\x12\x10\n\x0ckMtSubscribe\x10i\x12\x12\n\x0ekMtUnsubscribe\x10j\x12\x0e\n\nkMtPublish\x10k\x12\x10\n\x0ckMtQueryCode\x10l\x12\x13\n\x0fkMtQueryCodeAns\x10m\x12\x11\n\rkMtQueryKLine\x10n\x12\x14\n\x10kMtQueryKLineAns\x10o\x12\x14\n\x10kMtGetSecuMaster\x10p\x12\x17\n\x13kMtGetSecuMasterAns\x10q\x12\x11\n\rkMtMegatePing\x10r\x12\x11\n\rkMtMegatePong\x10s\x12\x19\n\x15kMtGetSecuMasterPrice\x10t\x12\x1c\n\x18kMtGetSecuMasterPriceAns\x10u\x12\x16\n\x12kMtGetSecuMasterV2\x10v\x12\x19\n\x15kMtGetSecuMasterV2Ans\x10w\x12\x15\n\x11kMtQueryRTHistory\x10x\x12\x18\n\x14kMtQueryRTHistoryAns\x10y\x12\x13\n\x0fkMtSubscribeAns\x10z\x12\x15\n\x11kMtUnSubscribeAns\x10{\x12\x1b\n\x17kMtGetSecuMasterFullist\x10|\x12\x1e\n\x1akMtGetSecuMasterFullistAns\x10}\x12\x13\n\x0fkMtCustomMsgPub\x10~\x12\x16\n\x12kMtCustomMsgPubAns\x10\x7f*\xed\x0c\n\x0c\x44gateMsgType\x12\r\n\tkDMtBegin\x10\x00\x12\x12\n\rkDMtSubscribe\x10\xd3\x0f\x12\x15\n\x10kDMtSubscribeAns\x10\xd4\x0f\x12\x14\n\x0fkDMtUnSubscribe\x10\xd5\x0f\x12\x17\n\x12kDMtUnSubscribeAns\x10\xd6\x0f\x12\x18\n\x13kDMtRequestDividend\x10\xd7\x0f\x12\x1b\n\x16kDMtRequestDividendAns\x10\xd8\x0f\x12\x1e\n\x19kDMtRequestCapitalization\x10\xd9\x0f\x12!\n\x1ckDMtRequestCapitalizationAns\x10\xda\x0f\x12\x18\n\x13kDMtRequestCalendar\x10\xdb\x0f\x12\x1b\n\x16kDMtRequestCalendarAns\x10\xdc\x0f\x12\x16\n\x11kDMtLFDQueryKLine\x10\xdd\x0f\x12\x19\n\x14kDMtLFDQueryKLineAns\x10\xde\x0f\x12\x16\n\x11kDMtKfkaStgMsgPub\x10\xdf\x0f\x12\x17\n\x12kDMtLFDCancelQuery\x10\xe0\x0f\x12\x1a\n\x15kDMtLFDCancelQueryAns\x10\xe1\x0f\x12\x1e\n\x19kDMtRequestIndexExmembers\x10\xe2\x0f\x12!\n\x1ckDMtRequestIndexExmembersAns\x10\xe3\x0f\x12\x16\n\x11kDMtRequestIncome\x10\xe4\x0f\x12\x19\n\x14kDMtRequestIncomeAns\x10\xe5\x0f\x12\x18\n\x13kDMtRequestCashflow\x10\xe6\x0f\x12\x1b\n\x16kDMtRequestCashflowAns\x10\xe7\x0f\x12\x1c\n\x17kDMtRequestBalanceSheet\x10\xe8\x0f\x12\x1f\n\x1akDMtRequestBalanceSheetAns\x10\xe9\x0f\x12\x1d\n\x18kDMtRequestTreasuryRates\x10\xea\x0f\x12 \n\x1bkDMtRequestTreasuryRatesAns\x10\xeb\x0f\x12\x16\n\x11kDMtServiceStatus\x10\xec\x0f\x12\x1e\n\x19kDMtRequestIndustriesCode\x10\xed\x0f\x12!\n\x1ckDMtRequestIndustriesCodeAns\x10\xee\x0f\x12\x1a\n\x15kDMtRequestSecumaster\x10\xef\x0f\x12\x1d\n\x18kDMtRequestSecumasterAns\x10\xf0\x0f\x12\x19\n\x14kDMtReqSessionLogout\x10\xf1\x0f\x12!\n\x1ckDMtRequestTradingSuspension\x10\xf2\x0f\x12$\n\x1fkDMtRequestTradingSuspensionAns\x10\xf3\x0f\x12\x1b\n\x16kDMtRequestDescription\x10\xf4\x0f\x12\x1e\n\x19kDMtRequestDescriptionAns\x10\xf5\x0f\x12\x1f\n\x1akDMtRequestContractMapping\x10\xf6\x0f\x12\"\n\x1dkDMtRequestContractMappingAns\x10\xf7\x0f\x12\x1f\n\x1akDMtRequestBondDescription\x10\xf8\x0f\x12\"\n\x1dkDMtRequestBondDescriptionAns\x10\xf9\x0f\x12 \n\x1bkDMtRequestBondFloatingrate\x10\xfa\x0f\x12#\n\x1ekDMtRequestBondFloatingrateAns\x10\xfb\x0f\x12 \n\x1bkDMtRequestBondShiborPrices\x10\xfc\x0f\x12#\n\x1ekDMtRequestBondShiborPricesAns\x10\xfd\x0f\x12\'\n\"kDMtRequestBondRepoAndlBLEODPrices\x10\xfe\x0f\x12*\n%kDMtRequestBondRepoAndlBLEODPricesAns\x10\xff\x0f\x12\x1d\n\x18kDMtRequestBondBenchmark\x10\x80\x10\x12 \n\x1bkDMtRequestBondBenchmarkAns\x10\x81\x10\x12\x1a\n\x15kDMtRequestBondCoupon\x10\x82\x10\x12\x1d\n\x18kDMtRequestBondCouponAns\x10\x83\x10\x12#\n\x1ekDMtRequestBondAccruedInterest\x10\x84\x10\x12&\n!kDMtRequestBondAccruedInterestAns\x10\x85\x10\x12\x12\n\rkDMtQueryData\x10\x86\x10\x12\x15\n\x10kDMtQueryDataAns\x10\x87\x10*g\n\nStgMsgType\x12\x14\n\x10kStgMsgTypeBegin\x10\x00\x12\x18\n\x13kStgMsgTypeJIUZHUAN\x10\xe9\x07\x12\x13\n\x0ekStgMsgTypeKDJ\x10\xea\x07\x12\x14\n\x0fkStgMsgTypeMACD\x10\xeb\x07*e\n\x0eSDSServiceType\x12\x13\n\x0fkMtServiceBegin\x10\x00\x12\x11\n\rkMtServiceLfd\x10\x01\x12\x16\n\x12kMtServiceBaseData\x10\x02\x12\x13\n\x0fkMtServiceKafka\x10\x06*M\n\x0f\x45nServiceStatus\x12\x11\n\rkStatusNormal\x10\x00\x12\x12\n\x0ekStatusOffline\x10\x01\x12\x13\n\x0fkStatusNotExist\x10\x02*\xca\x01\n\x08MarketId\x12\x15\n\x11MARKET_ID_INVALID\x10\x00\x12\x10\n\x0cMARKET_ID_SZ\x10\x01\x12\x10\n\x0cMARKET_ID_SH\x10\x02\x12\x11\n\rMARKET_ID_CFE\x10\x03\x12\x11\n\rMARKET_ID_SHF\x10\x04\x12\x11\n\rMARKET_ID_CZC\x10\x05\x12\x11\n\rMARKET_ID_DCE\x10\x06\x12\x11\n\rMARKET_ID_SGE\x10\x07\x12\x11\n\rMARKET_ID_SZB\x10\x08\x12\x11\n\rMARKET_ID_SHB\x10\t*\xaa\x03\n\x11SecurityMajorType\x12\x1e\n\x1aSECURITY_MAJOR_TYPE_NOTSET\x10\x00\x12\x1d\n\x19SECURITY_MAJOR_TYPE_STOCK\x10\x01\x12\x1c\n\x18SECURITY_MAJOR_TYPE_BOND\x10\x02\x12\x1c\n\x18SECURITY_MAJOR_TYPE_FUND\x10\x03\x12\x1c\n\x18SECURITY_MAJOR_TYPE_SPOT\x10\x04\x12$\n SECURITY_MAJOR_TYPE_MONEY_MARKET\x10\x05\x12\x1d\n\x19SECURITY_MAJOR_TYPE_INDEX\x10\x06\x12(\n$SECURITY_MAJOR_TYPE_VIRTUAL_CURRENCY\x10\x07\x12\x1e\n\x1aSECURITY_MAJOR_TYPE_FUTURE\x10\n\x12\x1e\n\x1aSECURITY_MAJOR_TYPE_OPTION\x10\x0b\x12\x1f\n\x1bSECURITY_MAJOR_TYPE_WARRANT\x10\x0c\x12,\n(SECURITY_MAJOR_TYPE_VARIETY_STOCK_OPTION\x10\x0f*\xe4\x01\n\x12SecurityTradeState\x12\x1f\n\x1bSECURITY_TRADE_STATE_UNKNOW\x10\x00\x12\x1f\n\x1bSECURITY_TRADE_STATE_NORMAL\x10\x01\x12%\n!SECURITY_TRADE_STATE_STOP_ALL_DAY\x10\x03\x12\'\n#SECURITY_TRADE_STATE_STOP_TEMPORARY\x10\x04\x12\x1d\n\x19SECURITY_TRADE_STATE_EXIT\x10\x05\x12\x1d\n\x19SECURITY_TRADE_STATE_STOP\x10\x06*\xe2\x01\n\nBrokerType\x12\x14\n\x10\x46ICC_BSN_UNKNOWN\x10\x00\x12\x0f\n\x0b\x46ICC_BSN_TP\x10\x01\x12\x11\n\rFICC_BSN_ICAP\x10\x02\x12\x11\n\rFICC_BSN_CBBJ\x10\x03\x12\x11\n\rFICC_BSN_TJXT\x10\x04\x12\x11\n\rFICC_BSN_PATR\x10\x05\x12\x11\n\rFICC_BSN_UYMB\x10\x06\x12\x0f\n\x0b\x46ICC_BSN_SH\x10\x0c\x12\x0f\n\x0b\x46ICC_BSN_SZ\x10\r\x12\x13\n\x0f\x46ICC_BSN_MARKET\x10{\x12\x17\n\x12\x46ICC_BSN_ANONYMOUS\x10\xe9\x07\x42\x17\n\x15\x63om.lhhj.common.protob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'type_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\025com.lhhj.common.proto'
  _SDSDATATYPE._serialized_start=31
  _SDSDATATYPE._serialized_end=391
  _SDSMSGTYPE._serialized_start=394
  _SDSMSGTYPE._serialized_end=1035
  _DGATEMSGTYPE._serialized_start=1038
  _DGATEMSGTYPE._serialized_end=2683
  _STGMSGTYPE._serialized_start=2685
  _STGMSGTYPE._serialized_end=2788
  _SDSSERVICETYPE._serialized_start=2790
  _SDSSERVICETYPE._serialized_end=2891
  _ENSERVICESTATUS._serialized_start=2893
  _ENSERVICESTATUS._serialized_end=2970
  _MARKETID._serialized_start=2973
  _MARKETID._serialized_end=3175
  _SECURITYMAJORTYPE._serialized_start=3178
  _SECURITYMAJORTYPE._serialized_end=3604
  _SECURITYTRADESTATE._serialized_start=3607
  _SECURITYTRADESTATE._serialized_end=3835
  _BROKERTYPE._serialized_start=3838
  _BROKERTYPE._serialized_end=4064
# @@protoc_insertion_point(module_scope)
