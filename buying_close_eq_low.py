from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr
import numpy as np
import pandas as pd
import quant

start_date = '2000-01-01'
df = openbb.stocks.load('QQQ', start_date = start_date)

df['daily_ret'] = df['Close'].pct_change(1)

def trade(df):
    
    df['trade'] = 0

    df['return_threshold'] = df['daily_ret'].rolling(510).std()
    cond_1 = df['daily_ret'] < - df['return_threshold'] # 당일 최근 2년 moving daily 수익률 기준 1표준편차 이상 하락
    
    cond_2 = abs(df['Low'] - df['Close']) < df['Close'] * 0.001 # 당일 저가가 종가 수준으로 마감

    df['trade'] = np.where(cond_1 & cond_2, 1, 0)

    df['trade'] = df['trade'].shift(1) # 종가매매시 다음날 수익률 적용

    return df

res = trade(df)
res['trade_ret'] = res.daily_ret * res.trade
res['cumret'] = quant.df_cumret(res.trade_ret, is_ret = True)

#1 ) win ratio

quant.win_rate(res['trade_ret'])