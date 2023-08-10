import pandas as pd
import numpy as np
from openbb_terminal.sdk import openbb

#1, 레버리지 X

# beautifulsoup scraping etf names / code

#%%

import FinanceDataReader as fdr
from datetime import datetime

path = "C:/Users/문희관/Desktop/etf_list.csv"

## etf price collection

etf_list = pd.read_csv(path, index_col = 0)
etf_code = etf_list.index.astype("str")

etf_price = {}

start_date = '2019-01-01'
end_date = '2023-08-09'

for i in etf_code:
    try:
        res = fdr.DataReader(i, start = start_date, end = end_date)
        res = res['Close']
        etf_price[i] = res

    finally:
        continue

dummy = pd.DataFrame(etf_price).to_csv("./etf_price.csv")


#%% 


def daily_ret(df):

    res = df.pct_change(1)
    return res

def cum_ret(df):

    df = daily_ret(df)
    res = (df + 1).cumprod() - 1
    return res

# %%

# 수익률 상관 높은거 추리기

path = "./etf_price.csv"
us_etf = 'DBB'
kr_etf = '160580'

df_price = pd.read_csv(path, index_col = 0)
df_price.index = pd.to_datetime(df_price.index)
df_ret = df_price.pct_change(1)

us_price = openbb.stocks.load(us_etf, start_date = start_date)
us_ret = us_price.pct_change(1)['Adj Close']

# 비교 selection

kr = cum_ret(df_price[[kr_etf]])
us = cum_ret(us_price['Adj Close'])

# 상관계수

corr = df_ret.corrwith(us_ret)
top_10 = corr.nlargest(10)

etf_list.loc[top_10.index.astype('int64')]
# %%



# %%
