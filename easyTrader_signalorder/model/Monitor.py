from model import Global_variables
from .MongoDB import MongoBase
import pandas
import datetime
import easytrader
import win32api
import win32con


def check_easytrader_connection():

    # easytrader断线重连兼仓位监测
    etBase = Global_variables.get_value("etBase")
    SClient = Global_variables.get_value("SClient")

    mg_position = MongoBase("amy_inside", "Arthur", "Position")
    try:
        start_balance = etBase.balance[0]
    except:
        try:
            try:
                etBase.exit()
                etBase = easytrader.use('yh_client')
                etBase.prepare(user='210400045979', password='668668', exe_path='C:\\中国银河证券双子星3.2\\xiadan.exe')
            except Exception as e:
                print(str(e))
                # 客户端无法自动登录时模拟enter按键登录
                win32api.keybd_event(13, 0, 0, 0)
                win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
            Global_variables.set_value("etBase", etBase)
            start_balance = etBase.balance[0]
        except Exception as e:
            print("cannot reconnect to easyTrader: ", str(e))
            Global_variables.set_value("connection_signal", 0)
            return 1
    StartPosition = pandas.DataFrame(etBase.position)
    StartPosition["start_or_end"] = "start"
    StartPosition["Date"] = str(datetime.datetime.today())
    Global_variables.set_value("StartPosition", StartPosition)
    mg_position.insertDB(StartPosition)

    print("while reached")
    while datetime.datetime.now().hour < 15:
        try:
            volume_signal = Global_variables.get_value("volume_signal")
            balance = etBase.balance[0]
            RtPosition = pandas.DataFrame(etBase.position)
            print("RtPosition:\n", RtPosition)
            Global_variables.set_value("RtPosition", RtPosition)
            if volume_signal:
                if balance["总市值"]/balance["总资产"] >= 0.8:
                    Global_variables.set_value("volume_signal", 0)
                    SClient.chat_postMessage(
                        channel="#quantitative-investment",
                        text="持仓过多"
                    )
                if balance["总市值"]/start_balance["总市值"] > 1.3:
                    Global_variables.set_value("volume_signal", 0)
                    SClient.chat_postMessage(
                        channel="#quantitative-investment",
                        text="持仓增加过快"
                    )
            if not volume_signal:
                if balance["总市值"]/balance["总资产"] < 0.8 and balance["总市值"]/StartPosition["总市值"] < 1.3:
                    Global_variables.set_value("volume_signal", 1)
                    SClient.chat_postMessage(
                        channel="#quantitative-investment",
                        text="解除持仓过多"
                    )
        except:
            etBase.exit()
            try:
                etBase = easytrader.use('yh_client')
                etBase.prepare(user='210400045979', password='668668', exe_path='C:\\中国银河证券双子星3.2\\xiadan.exe')
            except:
                # 客户端无法自动登录时模拟enter按键登录
                win32api.keybd_event(13, 0, 0, 0)
                win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
            Global_variables.set_value("etBase", etBase)
    end_position = pandas.DataFrame(etBase.position)
    end_position["start_or_end"] = "end"
    end_position["Date"] = str(datetime.datetime.now().date())
    mg_position.insertDB(end_position)


def check_wind_connection():

    # wind连接检测
    SClient = Global_variables.get_value("SClient")
    SnapshotData = Global_variables.get_value("SnapshotData")

    while (not len(SnapshotData.index)) or ("000300.SH" not in SnapshotData["security_code"]):
        pass
    while datetime.datetime.now().hour < 15:
        connection_signal = Global_variables.get_value("connection_signal")
        SnapshotData = Global_variables.get_value(["SnapshotData"])
        hs_index_df = SnapshotData.groupby("security_code")["000300.SH"]
        hs_index_price = list(hs_index_df["rt_last"])
        if hs_index_price[-1] == hs_index_price[-2] and hs_index_price[-2] == hs_index_price[-3]:
            Global_variables.set_value("connection_signal", 0)
            SClient.chat_postMessage(
                channel="#quantitative-investment",
                text="wind断线"
            )
        else:
            if not connection_signal:
                SClient.chat_postMessage(
                    channel="#quantitative-investment",
                    text="wind恢复连接"
                )
            Global_variables.set_value("connection_signal", 1)
