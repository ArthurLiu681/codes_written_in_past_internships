import pandas
import numpy
import datetime

bull_market_stock = pandas.read_excel(".\\stock data.xlsx", sheet_name="个股牛市")
bull_market_stock["日期_Date"] = bull_market_stock["日期_Date"].apply(lambda x:
                                                                  datetime.date(x.year, x.month, 1))
bull_market_index = pandas.read_excel(".\\stock data.xlsx", sheet_name="创业板指数牛市").\
    rename(columns={"交易日期_TrdDt": "日期_Date"})
bull_market_index["日期_Date"] = bull_market_index["日期_Date"].apply(lambda x:
                                                                  datetime.date(x.year, x.month, 1))

bull_market_comparison = pandas.DataFrame()
for stock, group in bull_market_stock.groupby("股票代码_Stkcd"):
    bull_market_comparison = bull_market_comparison.append(pandas.merge(group, bull_market_index, how="outer",
                                                                        on="日期_Date").fillna(method="ffill"))

formation_months = [1, 3, 6, 9, 12]
test_months = [6, 6, 12, 12, 12]
total_bull_months = list(bull_market_comparison["日期_Date"].value_counts().index)
total_bull_months.sort()
total_months = len(total_bull_months)

ni = 0
output = pandas.DataFrame()
factors_frame_complete = pandas.DataFrame()

for i_ft in range(5):
    temp_output = pandas.DataFrame()
    formation_month = formation_months[i_ft]
    test_month = test_months[i_ft]
    interval_length = formation_month + test_month
    best_factors_frame = pandas.DataFrame()
    worst_factors_frame = pandas.DataFrame()

    for interval_start in range(total_months - interval_length + 1):
        bull_stock_car = pandas.DataFrame()
        bull_start_date = total_bull_months[interval_start]
        bull_end_date = total_bull_months[interval_start+interval_length-1]
        interval_bull_stock = bull_market_comparison.loc[(bull_market_comparison["日期_Date"] >= bull_start_date) &
                                                         (bull_market_comparison["日期_Date"] <= bull_end_date)]

        for stock, group in interval_bull_stock.groupby("股票代码_Stkcd"):
            group.sort_values(by="日期_Date")
            bull_cr = group["月收益率"].apply(lambda x: x+1).cumprod()
            bull_index_cr = group["指数月收益率_IdxMonRet"].apply(lambda x: x+1).cumprod()
            group["car"] = bull_cr - bull_index_cr
            if formation_month in [1, 3]:
                bull_stock_car = bull_stock_car.append(pandas.DataFrame({"stock_code": stock,
                                                                         "formation_car": group["car"].iloc[
                                                                             formation_month - 1],
                                                                         "first_month_car": group["car"].iloc[
                                                                             formation_month],
                                                                         "second_month_car": group["car"].iloc[
                                                                             formation_month + 1],
                                                                         "third_month_car": group["car"].iloc[
                                                                             formation_month + 2],
                                                                         "fourth_month_car": group["car"].iloc[
                                                                             formation_month + 3],
                                                                         "fifth_month_car": group["car"].iloc[
                                                                             formation_month + 4],
                                                                         "sixth_month_car": group["car"].iloc[
                                                                             formation_month + 5],
                                                                         "seventh_month_car": 0,
                                                                         "eighth_month_car": 0,
                                                                         "ninth_month_car": 0,
                                                                         "tenth_month_car": 0,
                                                                         "eleventh_month_car": 0,
                                                                         "twelfth_month_car": 0},
                                                                        index=[bull_start_date]))
            else:
                bull_stock_car = bull_stock_car.append(pandas.DataFrame({"stock_code": stock,
                                                                         "formation_car": group["car"].iloc[
                                                                             formation_month - 1],
                                                                         "first_month_car": group["car"].iloc[
                                                                             formation_month],
                                                                         "second_month_car": group["car"].iloc[
                                                                             formation_month + 1],
                                                                         "third_month_car": group["car"].iloc[
                                                                             formation_month + 2],
                                                                         "fourth_month_car": group["car"].iloc[
                                                                             formation_month + 3],
                                                                         "fifth_month_car": group["car"].iloc[
                                                                             formation_month + 4],
                                                                         "sixth_month_car": group["car"].iloc[
                                                                             formation_month + 5],
                                                                         "seventh_month_car": group["car"].iloc[
                                                                             formation_month + 6],
                                                                         "eighth_month_car": group["car"].iloc[
                                                                             formation_month + 7],
                                                                         "ninth_month_car": group["car"].iloc[
                                                                             formation_month + 8],
                                                                         "tenth_month_car": group["car"].iloc[
                                                                             formation_month + 9],
                                                                         "eleventh_month_car": group["car"].iloc[
                                                                             formation_month + 10],
                                                                         "twelfth_month_car": group["car"].iloc[
                                                                             formation_month + 11]},
                                                                        index=[bull_start_date]))
        bull_stock_car = bull_stock_car.sort_values(by=["formation_car"], inplace=False)
        best_stocks = bull_stock_car.iloc[-int(len(bull_stock_car) * 0.1):]
        worst_stocks = bull_stock_car.iloc[:int(len(bull_stock_car) * 0.1)]
        temp_best_stocks = best_stocks.apply(numpy.mean, axis=0)
        temp_worst_stocks = worst_stocks.apply(numpy.mean, axis=0)
        best_factors_frame = best_factors_frame.append(pandas.DataFrame(temp_best_stocks.values,
                                                                        index=temp_best_stocks.index).T)
        worst_factors_frame = worst_factors_frame.append(pandas.DataFrame(temp_worst_stocks.values,
                                                                          index=temp_worst_stocks.index).T)

    n = len(best_factors_frame)

    ACAR_W_se = best_factors_frame.apply(numpy.mean, axis=0)
    ACAR_W = pandas.DataFrame(ACAR_W_se.values, index=ACAR_W_se.index).T.set_index(pandas.Index([i_ft]))
    ACAR_L_se = worst_factors_frame.apply(numpy.mean, axis=0)
    ACAR_L = pandas.DataFrame(ACAR_L_se.values, index=ACAR_L_se.index).T.set_index(pandas.Index([i_ft]))

    ACAR_W1 = ACAR_W["first_month_car"].iloc[0]
    ACAR_L1 = ACAR_L["first_month_car"].iloc[0]
    temp1 = sum(list(best_factors_frame["first_month_car"].apply(lambda x: (x - ACAR_W1) ** 2)))
    temp2 = sum(list((worst_factors_frame["first_month_car"].apply(lambda x: (x - ACAR_L1) ** 2))))
    s = (temp1 + temp2) / (2 * (n - 1))
    T1 = (ACAR_L1 - ACAR_W1) / (2 * s * s / n)
    output = output.append(pandas.DataFrame({"length_of_formation_period": formation_month,
                                             "length_of_test_period": test_month,
                                             "month_number": 1,
                                             "ACAR_W": ACAR_W1,
                                             "ACAR_L": ACAR_L1,
                                             "no_of_intervals": n,
                                             "s": s,
                                             "T": T1}, index=[s]))

    ACAR_W3 = ACAR_W["third_month_car"].iloc[0]
    ACAR_L3 = ACAR_L["third_month_car"].iloc[0]
    temp1 = sum(list(best_factors_frame["third_month_car"].apply(lambda x: (x - ACAR_W3) ** 2)))
    temp2 = sum(list((worst_factors_frame["third_month_car"].apply(lambda x: (x - ACAR_L3) ** 2))))
    s = (temp1 + temp2) / (2 * (n - 1))
    T3 = (ACAR_L3 - ACAR_W3) / (2 * s * s / n)
    output = output.append(pandas.DataFrame({"length_of_formation_period": formation_month,
                                             "length_of_test_period": test_month,
                                             "month_number": 3,
                                             "ACAR_W": ACAR_W3,
                                             "ACAR_L": ACAR_L3,
                                             "no_of_intervals": n,
                                             "s": s,
                                             "T": T3}, index=[s]))

    ACAR_W6 = ACAR_W["sixth_month_car"].iloc[0]
    ACAR_L6 = ACAR_L["sixth_month_car"].iloc[0]
    temp1 = sum(list(best_factors_frame["sixth_month_car"].apply(lambda x: (x - ACAR_W6) ** 2)))
    temp2 = sum(list((worst_factors_frame["sixth_month_car"].apply(lambda x: (x - ACAR_L6) ** 2))))
    s = (temp1 + temp2) / (2 * (n - 1))
    T6 = (ACAR_L6 - ACAR_W6) / (2 * s * s / n)
    output = output.append(pandas.DataFrame({"length_of_formation_period": formation_month,
                                             "length_of_test_period": test_month,
                                             "month_number": 6,
                                             "ACAR_W": ACAR_W6,
                                             "ACAR_L": ACAR_L6,
                                             "no_of_intervals": n,
                                             "s": s,
                                             "T": T6}, index=[s]))

    if formation_month in [6, 9, 12]:
        ACAR_W9 = ACAR_W["ninth_month_car"].iloc[0]
        ACAR_L9 = ACAR_L["ninth_month_car"].iloc[0]
        temp1 = sum(list(best_factors_frame["ninth_month_car"].apply(lambda x: (x - ACAR_W9) ** 2)))
        temp2 = sum(list((worst_factors_frame["ninth_month_car"].apply(lambda x: (x - ACAR_L9) ** 2))))
        s = (temp1 + temp2) / (2 * (n - 1))
        T9 = (ACAR_L9 - ACAR_W9) / (2 * s * s / n)
        output = output.append(pandas.DataFrame({"length_of_formation_period": formation_month,
                                                 "length_of_test_period": test_month,
                                                 "month_number": 9,
                                                 "ACAR_W": ACAR_W9,
                                                 "ACAR_L": ACAR_L9,
                                                 "no_of_intervals": n,
                                                 "s": s,
                                                 "T": T9}, index=[s]))

        ACAR_W12 = ACAR_W["twelfth_month_car"].iloc[0]
        ACAR_L12 = ACAR_L["twelfth_month_car"].iloc[0]
        temp1 = sum(list(best_factors_frame["twelfth_month_car"].apply(lambda x: (x - ACAR_W12) ** 2)))
        temp2 = sum(list((worst_factors_frame["twelfth_month_car"].apply(lambda x: (x - ACAR_L12) ** 2))))
        s = (temp1 + temp2) / (2 * (n - 1))
        T12 = (ACAR_L12 - ACAR_W12) / (2 * s * s / n)
        output = output.append(pandas.DataFrame({"length_of_formation_period": formation_month,
                                                 "length_of_test_period": test_month,
                                                 "month_number": 12,
                                                 "ACAR_W": ACAR_W12,
                                                 "ACAR_L": ACAR_L12,
                                                 "no_of_intervals": n,
                                                 "s": s,
                                                 "T": T12}, index=[s]))

    ACAR_W = ACAR_W.drop("stock_code", axis=1).rename(columns={"formation_car": "formation_car_W",
                                                               "first_month_car": "ACAR1_W",
                                                               "second_month_car": "ACAR2_W",
                                                               "third_month_car": "ACAR3_W",
                                                               "fourth_month_car": "ACAR4_W",
                                                               "fifth_month_car": "ACAR5_W",
                                                               "sixth_month_car": "ACAR6_W",
                                                               "seventh_month_car": "ACAR7_W",
                                                               "eighth_month_car": "ACAR8_W",
                                                               "ninth_month_car": "ACAR9_W",
                                                               "tenth_month_car": "ACAR10_W",
                                                               "eleventh_month_car": "ACAR11_W",
                                                               "twelfth_month_car": "ACAR12_W"})
    ACAR_W["formation_length"] = formation_month
    ACAR_W["test_length"] = test_month

    ACAR_L = ACAR_L.drop("stock_code", axis=1).rename(columns={"formation_car": "formation_car_L",
                                                               "first_month_car": "ACAR1_L",
                                                               "second_month_car": "ACAR2_L",
                                                               "third_month_car": "ACAR3_L",
                                                               "fourth_month_car": "ACAR4_L",
                                                               "fifth_month_car": "ACAR5_L",
                                                               "sixth_month_car": "ACAR6_L",
                                                               "seventh_month_car": "ACAR7_L",
                                                               "eighth_month_car": "ACAR8_L",
                                                               "ninth_month_car": "ACAR9_L",
                                                               "tenth_month_car": "ACAR10_L",
                                                               "eleventh_month_car": "ACAR11_L",
                                                               "twelfth_month_car": "ACAR12_L"})

    factors_frame_complete = factors_frame_complete.append(pandas.merge(ACAR_W, ACAR_L, left_index=True,
                                                                        right_index=True))

output.to_csv(".\\bull market t values.csv", index=False)
factors_frame_complete.to_csv(".\\bull market factor values.csv", index=False)
