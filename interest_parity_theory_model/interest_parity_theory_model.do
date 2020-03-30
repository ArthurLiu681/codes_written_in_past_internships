version 16

clear

log using "C:\Users\admin\Desktop\interest_parity_theory_model\interest_parity_theory_model.log", replace

python:

import pandas
import datetime
import numpy
from sfi import Data

# read data files and calculate factors

spot_exchange_rate_frame = pandas.read_csv("C:\\Users\\admin\\Desktop\\interest_parity_theory_model\\spot_exchange_rate_GBP-USD.csv")
libor_GBP_frame = pandas.read_csv("C:\\Users\\admin\\Desktop\\interest_parity_theory_model\\LIBOR_GBP_Monthly.csv")
libor_GBP_frame["Libor_GBP"] = libor_GBP_frame["Libor_GBP"].apply(lambda x: 1+(x/100))
libor_USD_frame = pandas.read_csv("C:\\Users\\admin\\Desktop\\interest_parity_theory_model\\LIBOR_USD_Monthly.csv")
libor_USD_frame["Libor_USD"] = libor_USD_frame["Libor_USD"].apply(lambda x: 1+(x/100))
factors_dependents_frame = pandas.merge(spot_exchange_rate_frame, libor_GBP_frame, on="Date")
factors_dependents_frame = pandas.merge(factors_dependents_frame, libor_USD_frame, on="Date")
factors_dependents_frame["Date"] = [datetime.datetime.strptime(date_string,"%m/%d/%Y")for date_string in list(factors_dependents_frame["Date"])]
factors_dependents_frame["Date"] = [str(datetime_date.year) + "/" + str(datetime_date.month) for datetime_date in list(factors_dependents_frame["Date"])]
factors_dependents_frame = factors_dependents_frame.groupby("Date").mean()

future_exchange_rate_frame = pandas.read_excel("C:\\Users\\admin\\Desktop\\interest_parity_theory_model\\future_exchange_rate_GBP-USD.xlsx", sheet_name="monthly")[["Date", "United Kingdom"]]
future_exchange_rate_frame["United Kingdom"] = future_exchange_rate_frame["United Kingdom"].apply(lambda x: 1/x)
future_exchange_rate_frame["Date"] = [datetime.datetime.strptime(date_string,"%Ym%m")for date_string in list(future_exchange_rate_frame["Date"])]
future_exchange_rate_frame["Date"] = [str(datetime_date.year) + "/" + str(datetime_date.month) for datetime_date in list(future_exchange_rate_frame["Date"])]

factors_dependents_frame = pandas.merge(factors_dependents_frame, future_exchange_rate_frame, on="Date")
factors_dependents_frame = factors_dependents_frame.iloc[[i for i in range(len(factors_dependents_frame.index)) if factors_dependents_frame["Date"].iloc[i].split("/")[0]>="1990"]]
factors_dependents_frame = factors_dependents_frame.dropna(axis=0, how="any")
factors_dependents_frame = factors_dependents_frame.iloc[[i for i in range(len(factors_dependents_frame.index)) if "NA" not in list(factors_dependents_frame.iloc[i])]]

factors_dependents_frame = factors_dependents_frame.set_index("Date")
factors_dependents_frame["y"] = factors_dependents_frame["United Kingdom"] - factors_dependents_frame["GBP/USD_spot"]

Data.addObs(len(factors_dependents_frame.index))
Data.addVarStr("Date", 7)
Data.addVarFloat("y")
Data.addVarFloat("x1")
Data.addVarFloat("x2")
Data.addVarFloat("y1")
Data.store("Date", None, list(factors_dependents_frame.reset_index("Date")["Date"]))
Data.store("y", None, list(factors_dependents_frame["y"]))
Data.store("x1", None, list(factors_dependents_frame["Libor_GBP"]))
Data.store("x2", None, list(factors_dependents_frame["Libor_USD"]))
Data.store("y1", None, list(factors_dependents_frame["United Kingdom"]))

end

* eda

gen mdate = monthly(Date, "YM")
tsset mdate, monthly
list mdate y D.y x1 D.x1 x2 D.x2 y1

gen x1p = x1 - 1
gen x2p = x2 - 1
graph twoway tsline y x1p x2p, legend(label(1 "Future - Spot") label(2 "Libor_GBP") label(3 "Libor_USD"))
graph export "C:\Users\admin\Desktop\interest_parity_theory_model\eda.pdf"

* regression analysis

reg y x1 x2

* ADF test


dfuller y, trend
dfuller D.y, trend
dfuller x1, trend
dfuller D.x1, trend
dfuller x2, trend
dfuller D.x2, trend

* VaR model

var y1 x1 x2, lags(1/2)

* Granger Causal Relation Test 

vargranger

* Johansen Test

vecrank y x1 x2, lags(11) trend(constant)

log close