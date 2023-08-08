#%% 
from dotenv import load_dotenv
import os
from fredapi import Fred
import pandas as pd

load_dotenv()
fred = Fred(api_key = os.environ.get('FRED_API'))

''' 
1) fred.get_series()
series_id = 'string' -> 홈페이지에서 이름 검색 필요
offset = 0 ~ nn -> 맨 위에서부터 삭제할 데이터 행 수 지정 default = 0
sort_order = 'asc' / 'desc' -> default 'asc'
observation_start = 'YYYY-MM-DD' string -> default 1700년대
observation_end = 'YYYY-MM-DD' string -> default 9999-12-31
unit = 
frequency = 'd' / 'w' / 'm' / 'y' 정도만 알면 됨  => grouping 후 agg 까지
+ aggregation_method = 'avg' / 'sum' / 'eop' -> default 'avg

'''

sp500 = fred.get_series('SP500', frequency = 'w')
sp500_2 = fred.get_series('SP500')

#%% interest rate

# 1) interest rate

dict_interest_rate = {
    't3m' : 'DGS3MO',
    't6m' : 'DGS6MO',
    't1' : 'DGS1',
    't2' : 'DGS2',
    't5' : 'DGS5',
    't7' : 'DGS7',
    't10' : 'DGS10',
    't20' : 'DGS20',
    't30' : 'DGS30'
}

def us_treasury(dict, start_date = None):
    
    dummy = []

    for i in dict_interest_rate.keys():
        dummy.append(fred.get_series(dict_interest_rate.get(i), observation_start = start_date))

    df_rate = pd.concat(dummy, axis = 1, join = 'outer')
    df_rate.columns = dict_interest_rate.keys()

    return df_rate

if __name__ == "__main__":
    rate = us_treasury(dict_interest_rate)

#%% 

import FinanceDataReader as fdr
import pandas as pd
import numpy as np

start_date = '2004-01-01'
end_date = '2021-09-30'
rf = 0

spy = fdr.DataReader("SPY", start = start_date, end = end_date)
spy_ret = spy['Adj Close'].pct_change(1).fillna(0)
spy_cum = (1 + spy_ret).cumprod() - 1

agg = fdr.DataReader("AGG", start = start_date, end = end_date)
agg_ret = agg['Adj Close'].pct_change(1).fillna(0)
agg_cum = (1 + agg_ret).cumprod() - 1

w_spy = 0.6
w_agg = 0.4

mix_ret = spy_ret * w_spy + agg_ret * w_agg
mix_cum = (1 + mix_ret).cumprod() - 1

mix_ret_cum = mix_cum[-1]
mix_cagr = np.power((1 + mix_ret_cum), 252/len(mix_cum.index)) - 1
mix_vol = np.std(mix_ret) * np.sqrt(252)
mix_sharpe = (mix_cagr - rf) / mix_vol

# %%
