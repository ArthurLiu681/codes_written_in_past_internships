from model.MongoDB import mongocol_to_dataframe
from model.EasyTrader_functions import Quote
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from model.Security_types import Stock, StockList, Bond, BondList, Etf, EtfList
import pandas
import easytrader
import win32api
import win32con
import slack
from model.MongoDB import MongoBase


def _init():
    global _global_dict
    _global_dict = {}


def set_value(name, value):
    _global_dict[name] = value


def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue


# 定义全局变量
try:
    etBase = easytrader.use('yh_client')
    etBase.prepare(user='210400045979', password='668668', exe_path='C:\\中国银河证券双子星3.2\\xiadan.exe')
except Exception as e:
    # 客户端无法自动登录时模拟enter按键登录
    print(str(e))
    win32api.keybd_event(13, 0, 0, 0)
    win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)

quote = Quote()
volume_signal = 1
connection_signal = 1

# stock_list = StockList([Stock("000001.SZ")])
Bond_list = BondList([Bond("113009.SH")])
# Etf_list = EtfList([Etf("159920.SZ")])
all_securities = Bond_list.traders

MB_Snap_stock = MongoBase("amy_inside", "Arthur", "Quote_Stock")
MB_Snap_bond = MongoBase("amy_inside", "Arthur", "Quote_Bond")
MB_Snap_etf = MongoBase("amy_inside", "Arthur", "Quote_Etf")
InitialDF_stock = mongocol_to_dataframe(MB_Snap_stock.collection.find())
InitialDF_bond = mongocol_to_dataframe(MB_Snap_bond.collection.find())
InitialDF_etf = mongocol_to_dataframe(MB_Snap_etf.collection.find())
InitialDF = pandas.concat([pandas.DataFrame()] +
                          [df for df in [InitialDF_stock, InitialDF_bond, InitialDF_etf] if len(df.index)])
if len(InitialDF.index):
    del InitialDF["_id"]
    InitialDF = InitialDF[InitialDF["security_code"].isin([security.code for security in all_securities])]
    InitialDF = InitialDF.sort_index(by=["Time"], ascending=True)
    if len(InitialDF.index) > len(all_securities) * 3602:
        InitialDF = InitialDF.iloc[-len(all_securities) * 3602:]
SnapshotData = InitialDF

MB_HOLC_stock = MongoBase("amy_inside", "Arthur", "HOLC_Stock")
MB_HOLC_bond = MongoBase("amy_inside", "Arthur", "HOLC_Bond")
MB_HOLC_etf = MongoBase("amy_inside", "Arthur", "HOLC_Etf")
InitialDF_stock = mongocol_to_dataframe(MB_HOLC_stock.collection.find())
InitialDF_bond = mongocol_to_dataframe(MB_HOLC_bond.collection.find())
InitialDF_etf = mongocol_to_dataframe(MB_HOLC_etf.collection.find())
InitialDF = pandas.concat([pandas.DataFrame()] +
                          [df for df in [InitialDF_stock, InitialDF_bond, InitialDF_etf] if len(df.index)])
if len(InitialDF.index):
    del InitialDF["_id"]
    InitialDF = InitialDF[InitialDF["security_code"].isin([security.code for security in all_securities])]
    InitialDF = InitialDF.sort_index(by=["date"], ascending=True)
    if len(InitialDF.index) > len(all_securities) * 22:
        InitialDF = InitialDF.iloc[-len(all_securities) * 22:]
HOLCData = InitialDF

StartPosition = pandas.DataFrame()
RtPosition = pandas.DataFrame()
SClient = slack.WebClient(token="xoxp-867150974242-869678516449-879976704581-4362de6284802dd309d99adaf18bcbd9")
executors = {
    "default": ThreadPoolExecutor(100),
    "processpool": ProcessPoolExecutor(100)
}
job_defaults = {
    "coalesce": False,
    "max_instances": 100
}
scheduler = BlockingScheduler(job_defaults=job_defaults, executors=executors)

_init()
set_value("etBase", etBase)
set_value("quote", quote)
set_value("volume_signal", volume_signal)
set_value("connection_signal", connection_signal)
set_value("SnapshotData", SnapshotData)
set_value("StartPosition", StartPosition)
set_value("RtPosition", RtPosition)
set_value("SClient", SClient)
set_value("scheduler", scheduler)
set_value("HOLCData", HOLCData)
set_value("all_securities", all_securities)
