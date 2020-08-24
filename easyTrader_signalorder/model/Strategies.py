from model import Global_variables
import threading
import datetime
import pandas
from model.EasyTrader_functions import Order
from model.MongoDB import mongocol_to_dataframe
import numpy
from chinese_calendar import is_workday


def get_snapshot_data():

    # 获取行情信息
    print("snapshotdata start: {}".format(str(datetime.datetime.now())))
    quote = Global_variables.get_value("quote")
    SnapshotData = Global_variables.get_value("SnapshotData")
    all_securities = Global_variables.get_value("all_securities")

    temp_df = quote.get_snapshot(all_securities)
    SnapshotData = pandas.concat([SnapshotData, temp_df])
    if len(SnapshotData.index) > 3602 * len(all_securities):
        SnapshotData = SnapshotData.iloc[len(all_securities):]
    Global_variables.set_value("SnapshotData", SnapshotData)
    print("snapshotdata ends: {}".format(str(datetime.datetime.now())))


def get_holc_data():

    # 获取高开低收
    all_securities = Global_variables.get_value("all_securities")
    HOLCData = Global_variables.get_value("HOLCData")
    quote = Global_variables.get_value("quote")
    if not len(mongocol_to_dataframe(quote.MB_holc_Stock.collection.find()).index):
        query_dates = []
        i = 2
        while len(query_dates) < 21:
            print("length of query dates: {}".format(len(query_dates)))
            query_date = datetime.datetime.today() - datetime.timedelta(days=i)
            if is_workday(query_date):
                query_dates.append(query_date)
            i = i + 1
        for query_date in reversed(query_dates):
            query_date = datetime.datetime.strftime(query_date, '%Y%m%d')
            wind_data = quote.get_ohlc(all_securities, query_date)
            HOLCData = pandas.concat([HOLCData, wind_data])
            Global_variables.set_value("HOLCData", HOLCData)
    if max(HOLCData["date"]) != datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days=1), '%Y%m%d'):
        wind_data = quote.get_ohlc(all_securities, datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days=1), '%Y%m%d'))
        HOLCData = pandas.concat([HOLCData, wind_data])
    if len(HOLCData.index) > 22 * len(all_securities):
        HOLCData = HOLCData.iloc[len(all_securities):]
    Global_variables.set_value("HOLCData", HOLCData)


def order_by_signal(security_code, f, signal):

    etBase = Global_variables.get_value("etBase")
    SClient = Global_variables.get_value("SClient")
    connection_signal = Global_variables.get_value("connection_signal")
    volume_signal = Global_variables.get_value("volume_signal")
    StartPosition = Global_variables.get_value("StartPosition")
    RtPosition = Global_variables.get_value("RtPosition")
    SnapshotData = Global_variables.get_value("SnapshotData")
    security_data = SnapshotData[SnapshotData["security_code"] == security_code]
    price = numpy.mean(security_data["RT_LAST"])
    while not list(RtPosition.columns):
        RtPosition = Global_variables.get_value("RtPosition")
    if connection_signal:
        if signal == "buy":
            if volume_signal:
                # 个股持仓增长超过100%时停止买入
                position = list(RtPosition[RtPosition["证券代码"] == ".".split(security_code)[0]]["参考市值"])[0]
                start_position = list(StartPosition[StartPosition["证券代码"] == ".".split(security_code)[0]]["参考市值"])[0]
                if position < 2 * start_position:
                    order = Order(security_code, "buy", 100, price=price * 0.99)
                    ord = order.make_order(etBase)
                    f.write(str(ord))
                else:
                    SClient.chat_postMessage(
                        channel="#quantitative-investment",
                        text="{}持仓增长过快".format(security_code)
                    )
        elif signal == "sell":
            if ".".split(security_code)[0] in list(RtPosition["证券代码"]):
                order = Order(security_code, "sell", 100, price=price * 1.01)
                ord = order.make_order(etBase)
                f.write(str(ord))


def order_by_mas(f):

    # 根据moving average signal下单

    def mas_calcu(prices, volumes):
        total_volume = sum(volumes)
        return sum([prices[i] * volumes[i]/total_volume for i in range(len(prices))])

    def mas(group):
        # 计算moving average信号
        pre_price_list = list(group["RT_LAST"].iloc[(-3602):(-2)])
        pre_volume_list = list(group["RT_LAST_VOL"].iloc[(-3602):(-2)])
        pre_average = mas_calcu(pre_price_list, pre_volume_list)
        pre_pri = group["RT_LAST"].iloc[-2]
        cur_price_list = list(group["RT_LAST"].iloc[(-3601):(-1)])
        cur_volume_list = list(group["RT_LAST_VOL"].iloc[(-3601):(-1)])
        cur_average = mas_calcu(cur_price_list, cur_volume_list)
        cur_pri = group["RT_LAST"].iloc[-1]
        f.write("strategy: moving_average; time: {}; pre_aver_price: {}; pre_price: {}; cur_aver_price: {}; "
                "cr_price: {}; ".format(str(max(group["Time"])), pre_average, pre_pri, cur_average, cur_pri))
        print("mas end: {}".format(str(datetime.datetime.now())))
        if cur_pri > cur_average and pre_pri < pre_average:
            return "sell"
        elif cur_pri < cur_average and pre_pri > pre_average:
            return "buy"
        else:
            return "no_action"

    def mas_order(security_code, group):
        signal = mas(group)
        f.write("signal: {}\n".format(signal))
        if signal != "no_action":
            order_by_signal(security_code, f, signal)

    print("mas start: {}".format(str(datetime.datetime.now())))
    snapshotdata = Global_variables.get_value("SnapshotData")
    all_securities = Global_variables.get_value("all_securities")
    print("length of snapshotdata in strategies:", len(snapshotdata.index))
    if len(snapshotdata.index) < 3602 * len(all_securities):
        print("waiting")
        return 0
    f.write("snapshotdata: \n{}\n".format(snapshotdata))
    for security_code, group in snapshotdata.groupby("security_code"):
        if list(group["security_type"])[0] == "Bond":
            f.write("security: {}\n".format(security_code))
            thread = threading.Thread(target=mas_order, args=(security_code, group, ))
            thread.start()


def order_by_time_signal(f):

    # 按照时间信号下单
    all_securities = Global_variables.get_value("all_securities")

    def time_order(security_code):
        order_by_signal(security_code, f, signal="buy")

    for security in all_securities:
        if security.security == "Stock":
            thread = threading.Thread(target=time_order, args=(security.code, ))
            thread.start()


def order_by_bollinger(f):

    # 按照布林通道策略下单
    HOLCData = Global_variables.get_value("HOLCData")

    while not len(HOLCData.index) or list(HOLCData["date"])[-1] != datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days=1), "%Y%m%d"):
        HOLCData = Global_variables.get_value("HOLCData")
    for security_code, group in HOLCData.groupby("security_code"):
        print(group)
        if list(group["security_type"])[0] == "Bond":
            high_price = list(group["HIGH"])
            low_price = list(group["LOW"])
            close_price = list(group["CLOSE"])
            price_factor = [numpy.mean([high_price[i], low_price[i], close_price[i]]) for i in range(len(high_price))]
            pre_aver = numpy.mean(price_factor[:(-2)])
            pre_sd = numpy.std(price_factor[:(-2)])
            pre_upper = pre_aver + 2 * pre_sd
            pre_lower = pre_aver - 2 * pre_sd
            cur_aver = numpy.mean(price_factor[1:(-1)])
            cur_sd = numpy.std(price_factor[1:(-1)])
            cur_upper = cur_aver + 2 * cur_sd
            cur_lower = cur_aver - 2 * cur_sd
            pre_price = price_factor[-2]
            cur_price = price_factor[-1]
            if pre_price < pre_upper and cur_price > cur_upper:
                signal = "sell"
            elif pre_price > pre_lower and cur_price < cur_lower:
                signal = "buy"
            else:
                signal = "no_action"
            print(pre_price, pre_lower, pre_upper, cur_price, cur_lower, cur_upper)
            order_by_signal(security_code, f, signal)


def order_by_rsi(f):

    # 按照rsi反转下单
    HOLCData = Global_variables.get_value("HOLCData")

    while not len(HOLCData.index) or list(HOLCData["date"])[-1] != datetime.datetime.strftime(datetime.datetime.today() - datetime.timedelta(days=1), "%Y%m%d"):
        HOLCData = Global_variables.get_value("HOLCData")

    for security_code, group in HOLCData.groupby("security_code"):
        if list(group["security_type"])[0] == "Stock":
            close_price = HOLCData["CLOSE"]
            change_list = list(close_price.diff())
            rise_list = [max(change, 0) for change in change_list]
            pre_ratio_rise_list = rise_list[(-21):(-1)]
            pre_ratio_change_list = change_list[(-21):(-1)]
            pre_rsi_ratio = numpy.mean(pre_ratio_rise_list) / numpy.mean([numpy.abs(change) for change in pre_ratio_change_list])
            cur_ratio_rise_list = rise_list[:(-20)]
            cur_ratio_change_list = change_list[:(-20)]
            cur_rsi_ratio = numpy.mean(cur_ratio_rise_list)/numpy.mean([numpy.abs(change) for change in cur_ratio_change_list])

            pre_short_rise_list = rise_list[(-7):(-1)]
            pre_short_change_list = change_list[(-7):(-1)]
            pre_short_rsi_ratio = numpy.mean(pre_short_rise_list) / numpy.mean(
                [numpy.abs(change) for change in pre_short_change_list])
            pre_long_rise_list = rise_list[(-13):(-1)]
            pre_long_change_list = change_list[(-12):]
            pre_long_rsi_ratio = numpy.mean(pre_long_rise_list) / numpy.mean(
                [numpy.abs(change) for change in pre_long_change_list])
            cur_short_rise_list = rise_list[(-6):]
            cur_short_change_list = change_list[(-6):]
            cur_short_rsi_ratio = numpy.mean(cur_short_rise_list)/numpy.mean(
                [numpy.abs(change) for change in cur_short_change_list])
            cur_long_rise_list = rise_list[(-12):]
            cur_long_change_list = change_list[(-12):]
            cur_long_rsi_ratio = numpy.mean(cur_long_rise_list) / numpy.mean(
                [numpy.abs(change) for change in cur_long_change_list])

            if cur_rsi_ratio < 0.3 < pre_rsi_ratio:
                signal = "buy"
            elif pre_rsi_ratio < 0.7 < cur_rsi_ratio:
                signal = "sell"
            else:
                if pre_short_rsi_ratio < pre_long_rsi_ratio and cur_short_rsi_ratio > cur_long_rsi_ratio:
                    signal = "buy"
                elif pre_short_rsi_ratio > pre_long_rsi_ratio and cur_short_rsi_ratio < cur_long_rsi_ratio:
                    signal = "sell"
                else:
                    signal = "no_action"
            print("rsi:", signal)
            order_by_signal(security_code, f, signal)
