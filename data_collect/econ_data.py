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
