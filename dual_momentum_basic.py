from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import quant
import util
import backtesting as bt
import pandas as pd
import numpy as np
from datetime import datetime as dt

df = pd.DataFrame()

start_date = '2010-01-01'
stocks = ['SPY', 'AAPL', 'MSFT', 'TLT', 'JPM', 'BAC', 'MRNA', 'META', 'WMT', 'BIL']
df = util.load_stock(stocks)

# momentum_score 계산

def momentum(df, interval = "M", list_months : list = [1, 3, 6, 12]):

    df_dummy = pd.DataFrame()
    for i in list_months:
        df_dummy[f"ret_{i}"] = df.resample(interval).\
            last().\
            dropna().\
            pct_change(i)
    df_dummy.index = util.extract_last_price(df, interval = interval).index

    dummy = list(reversed(list_months))
    
    res = df_dummy.loc[:, f'ret_{list_months[0]}': ].mul(dummy, axis = 1)
    res = res.sum(axis = 1) / sum(list_months)
    return res

df_momentum_score = df.apply(momentum)

#1. absolute momentum
df_abs_momentum = df_momentum_score.apply(lambda x : np.where(x > 0, 1 , 0)) # 공매도 없이 롱만 취한다는 가정 하여 abs momentum > 0

# 2. relative momentum 
def rank_function(score, top_n = 3):
    rank = score.rank(axis = 1, method = 'max', ascending = "False")
    selected_rank = rank.where(rank > len(stocks) - top_n, 0)
    return selected_rank

df_momentum_rank = rank_function(df_momentum_score)

#3. 변동성
def volatility(df, interval = 'D', list_months : list = [20, 60, 126, 252]):

    df_dummy = pd.DataFrame()

    for i in list_months:
        df_dummy[f'vol_{i}'] = df.\
            pct_change(1).\
            rolling(i).\
            std() * np.sqrt(252)

    dummy = list(reversed(list_months))
    res = df_dummy.loc[:, f'vol_{list_months[0]}': ].mul(dummy, axis = 1)
    res = res.sum(axis = 1) / sum(list_months)
    return res

df_vol_score = df.apply(volatility)
df

#4. correlation score : sum of all the correl coefficient wrt other assets

df_correl = df.pct_change(1).corr().sum() - 1

    
def put_trade(df : pd.DataFrame):
    
    df['trade'] = 0

    for i in df.index:
        prev_position = df['trade'].shift(1).loc[i]

        if prev_position == 0: # 이전에 무포지션이면,
            if df.loc[i, 'abs_momentum'] == 1: # 모멘텀 1이면
                df.loc[i, 'trade'] = 1 # 매수
            else:
                df.loc[i, 'trade'] = prev_position # 아니면 패스

        elif prev_position != 0: # 이전에 포지션 있으면
            if df.loc[i, 'abs_momentum']  == 0: # 모멘텀 0이면
                df.loc[i, 'trade'] = 0 # 청산
            else:
                df.loc[i, 'trade'] = prev_position # 기존 포지션 유지
            
    # 2) 결과론적인 성과평가이므로 trade 는 종가에 들어갔다고 가정 -> 실제 성과는 한 row씩 shift

    df['trade'] = df['trade'].shift(1)

    return df

res = df.pipe(abs_momentum).pipe(put_trade)

def get_return(df):
    daily_ret = df['close'].pct_change(1) * df['trade']
    cumret = quant.df_cumret(daily_ret, is_ret = True)
    return cumret
    