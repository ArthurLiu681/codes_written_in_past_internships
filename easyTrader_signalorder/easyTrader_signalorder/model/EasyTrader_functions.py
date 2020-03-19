from WindPy import *
from .MongoDB import mongocol_to_dataframe, MongoBase
import datetime
import pandas


# 封装easytrader中下单、改单和撤单函数，并按要求返回特定值，同时将新下单存入mongodb数据库
class Order(object):

    MB = MongoBase("amy_inside", "Arthur", "Order")
    all_orders = []

    def __init__(self, security_code, buy_or_sell, lot_size, price="market_price"):

        if buy_or_sell not in ["buy", "sell"]:
            raise Exception("Parameter for the second argument must be 'buy' or 'sell'")

        self.security_code = security_code
        self.buy_or_sell = buy_or_sell
        self.price = price
        self.lot_size = lot_size

    def make_order(self, etBase):

        self.order_time = datetime.datetime.now()

        try:
            if self.price != "market_price":
                if self.buy_or_sell == "sell":
                    id_dict = etBase.sell(self.security_code, self.price, self.lot_size)
                else:
                    id_dict = etBase.buy(self.security_code, self.price, self.lot_size)
            else:
                if self.buy_or_sell == "sell":
                    id_dict = etBase.market_sell(self.security_code, self.lot_size)
                else:
                    id_dict = etBase.market_buy(self.security_code, self.lot_size)
            self.id = id_dict['entrust_no']
            self.status = "success"
            print("order {}: {} {} {}".format(self.id, self.buy_or_sell, self.lot_size, self.security_code))

        except Exception as e:
            self.id = "nan"
            self.status = e
            print("{} {} {} {}".format(self.id, self.buy_or_sell, self.lot_size, self.security_code, self.status))
        self.series_no = len(Order.all_orders) + 1
        Order.all_orders.append(self)
        Order.MB.insertDB(pandas.DataFrame([[self.series_no, self.id, self.buy_or_sell, self.security_code, self.lot_size,
                                             self.status]], columns=["series_no", "id", "buy_or_sell", "security_code",
                                                                     "lot_size", "status"]))
        return {"order{}".format(self.id): {"buy_or_sell": self.buy_or_sell, "price": self.price, "lot_size": self.lot_size, "status": self.status}}

    def modify_order(self, etBase, security_code=True, buy_or_sell=True, lot_size=True, price=True):

        if buy_or_sell not in ["buy", "sell"]:
            raise Exception("Parameter for the second argument must be 'buy' or 'sell'")
        Order.MB.collection.update_one({"series_no": self.series_no}, {"$set": {"$status": "modified"}})
        try:
            etBase.cancel_entrust(self.id)
        finally:
            if not security_code:
                self.security_code = security_code
            if not buy_or_sell:
                self.buy_or_sell = buy_or_sell
            if not lot_size:
                self.lot_size = lot_size
            if not price:
                self.price = price
            self.make_order(etBase)

    def cancel_order(self, etBase):
        if self.id == 'nan':
            print("Invalid order already!")
        else:
            etBase.cancel_entrust(self.id)
        self.status = "cancelled"
        Order.MB.collection.update_one({"series_no": self.series_no}, {"$set": {"status": "cancelled"}})
        return {"order{}".format(self.id): {"buy_or_sell": self.buy_or_sell, "price": self.price, "lot_size": self.lot_size, "status": self.status}}


# 订单查询和状态刷新
class OrderList(object):

    all_order = mongocol_to_dataframe(Order.MB.collection.find())
    if not len(all_order.index):
        all_order = pandas.DataFrame(columns=["_id", "series_no", "id", "buy_or_sell", "security_code", "lot_size", "status"])

    pending_order = all_order[(all_order["status"] == "success") & (all_order["id"] != "nan")]
    
    @classmethod
    def filter_equal(cls, arg, param, etBase):
        OrderList.update(etBase)
        return OrderList.pending_order[OrderList.pending_order[arg] == param]
    
    @classmethod
    def filter_between(cls, arg, param1, param2, etBase):
        OrderList.update(etBase)
        return OrderList.pending_order[param1 < OrderList.pending_order[arg] < param2]

    @classmethod
    def cancel_all(cls, etBase):
        OrderList.update(etBase)
        for entrust_no in list(OrderList.pending_order["id"]):
            try:
                etBase.cancel_entrust(entrust_no)
                print("entrust {} cancelled successfully".format(entrust_no))
                Order.MB.collection.update_one({"id": entrust_no}, {"$set": {"status": "cancelled"}})
            except Exception as e:
                print("{} cancellation unsuccessful: {}".format(entrust_no, str(e)))
                Order.MB.collection.update_one({"id": entrust_no},
                                               {"$set": {"status": "cancellation unsuccessful: {}".format(str(e))}})
    
    @classmethod
    def update(cls, etBase):
        trades = etBase.today_trades
        if trades:
            trades_df = pandas.DataFrame(trades, index=range(len(trades)))
            for entrust_no in OrderList.pending_order["id"]:
                if entrust_no in trades_df["委托序号"]:
                    Order.MB.collection.update_one({"id": entrust_no},
                                                   {"$set": {"status": "traded"}})
        OrderList.all_order = mongocol_to_dataframe(Order.MB.collection.find())
        if not len(OrderList.all_order.index):
            OrderList.all_order = pandas.DataFrame(
                columns=["_id", "series_no", "id", "buy_or_sell", "security_code", "lot_size", "status"])
        OrderList.pending_order = OrderList.all_order[(OrderList.all_order["status"] == "success") & (OrderList.all_order["id"] != "nan")]


class Status(object):

    def get_position(self, etBase):
        return etBase.position

    def get_balance(self, etBase):
        return etBase.balance


# 从wind中获取实时行情
class Quote(object):

    MB_Stock = MongoBase("amy_inside", "Arthur", "Quote_Stock")
    MB_Bond = MongoBase("amy_inside", "Arthur", "Quote_Bond")
    MB_Etf = MongoBase("amy_inside", "Arthur", "Quote_Etf")
    MB_Fund = MongoBase("amy_inside", "Arthur", "Quote_Fund")
    MB_holc_Stock = MongoBase("amy_inside", "Arthur", "HOLC_Stock")
    MB_holc_Bond = MongoBase("amy_inside", "Arthur", "HOLC_Bond")
    MB_holc_Etf = MongoBase("amy_inside", "Arthur", "HOLC_Etf")
    MB_holc_Fund = MongoBase("amy_inside", "Arthur", "HOLC_Fund")

    def __init__(self):
        w.start()

    def get_snapshot(self, all_securities):
        wind_data = w.wsq([security.code for security in all_securities],
                          "rt_bid1,rt_ask1,rt_last,rt_bsize1,rt_asize1,rt_last_vol")
        if wind_data.ErrorCode:
            print(wind_data.ErrorCode)
            return pandas.DataFrame()
        temp_out_df = pandas.DataFrame(wind_data.Data).T
        temp_out_df.columns = wind_data.Fields
        temp_out_df["security_code"] = wind_data.Codes
        temp_out_df["Time"] = str(wind_data.Times[0])
        temp_out_df["security_type"] = [security.security for security in all_securities]
        for name, group in temp_out_df.groupby("security_type"):
            if name == "Stock":
                Quote.MB_Stock.insertDB(group)
            if name == "Bond":
                Quote.MB_Bond.insertDB(group)
            if name == "Etf":
                Quote.MB_Etf.insertDB(group)
            if name == "Fund":
                Quote.MB_Fund.insertDB(group)

        print("wind snapshotdata success!")
        return temp_out_df

    def get_ohlc(self, all_securities, date):

        # 获取高开低收价格
        wind_data = w.wss([security.code for security in all_securities], "open,high,low,close",
                          "tradeDate={};priceAdj=U;cycle=D".format(date))
        if wind_data.ErrorCode:
            print(wind_data.ErrorCode)
            return pandas.DataFrame()
        temp_out_df = pandas.DataFrame(wind_data.Data).T
        temp_out_df.columns = wind_data.Fields
        temp_out_df["security_code"] = wind_data.Codes
        temp_out_df["date"] = date
        temp_out_df["security_type"] = [security.security for security in all_securities]
        for name, group in temp_out_df.groupby("security_type"):
            if name == "Stock":
                Quote.MB_holc_Stock.insertDB(group)
            if name == "Bond":
                Quote.MB_holc_Bond.insertDB(group)
            if name == "Etf":
                Quote.MB_holc_Etf.insertDB(group)
            if name == "Fund":
                Quote.MB_holc_Fund.insertDB(group)
        print("wind HOLC success!")
        return temp_out_df
