class Trader(object):

    def __init__(self, code, exchange="does_not_matter", amount=50, max_amount=50):
        self.code = code
        self.exchange = exchange
        self.amount = amount
        self.maxAmount = max_amount
        self.appraiseRate = 0


class TraderList(object):

    def __init__(self, traders):
        self.traders = traders

    def get_code_arr(self):
        return [v.code for v in self.traders]

    def get_code_arr_with_exchange_type(self):
        return [v.code + "." + v.exchange for v in self.traders]

    def to_string_with_exchange_type(self):
        cl = self.get_code_arr_with_exchange_type()
        return ",".join(cl)

    def code_with_amount_dict(self):
        return {v.code: {"amount": v.amount, "maxAmount": v.maxAmount} for v in self.traders}

    # def codeWithAmountDict(self):
    #     return {v.code: v.amount for v in self.traders}

    def rate_appraise(self, cancel_entrusts_arr):
        for stockCode in self.traders:
            if stockCode.code in cancel_entrusts_arr:
                stockCode.appraiseRate += 1
            else:
                stockCode.appraiseRate = 0

    def get_appraise_rate(self, code):
        for v in self.traders:
            if v.code == code:
                return v.appraiseRate
        return 0

    def print(self):
        for stockCode in self.traders:
            print("code:%s, appraiseRate=%i, amount=%i" % (stockCode.code, stockCode.appraiseRate, stockCode.amount))


# 股票
class Stock(Trader):
    security = 'Stock'


# 转债
class Bond(Trader):
    security = 'Bond'


# ETF
class Etf(Trader):
    security = 'Etf'


# 基金
class Fund(Trader):
    security = 'Fund'


# 股票列表
class StockList(TraderList):
    security = "Stock"


# 转债列表
class BondList(TraderList):
    security = "Bond"


# ETF列表
class EtfList(TraderList):
    security = "Etf"


# 基金列表
class FundList(TraderList):
    security = "Fund"
