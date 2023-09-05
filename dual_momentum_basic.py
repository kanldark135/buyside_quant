from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import quant
import func
import backtesting as bt
import pandas as pd
import numpy as np
from datetime import datetime as dt

df = pd.DataFrame()

start_date = '2009-01-01'
stocks = ['SPY', 'AAPL', 'MSFT', 'TLT', 'JPM', 'BAC', 'MRNA', 'META', 'WMT', 'BIL']
df = func.load_stocks(stocks, drop_na_date = True, start_date = start_date)

# momentum_score 계산
def momentum_score(df, resample_by = "M", interval : list = [1, 3, 6, 12]):
    
    dummy = list(reversed(interval))
    df_dummy = pd.DataFrame()
    for int in interval:
        df_dummy[f"ret_{int}"] = df.resample(resample_by) \
            .last() \
            .dropna(how = 'all') \
            .pct_change(int)
    df_dummy.index = func.extract_last_price(df, interval = resample_by).index
    res = df_dummy.mul(dummy, axis = 1)
    res = res.sum(axis = 1) / sum(interval)
    return res

df_momentum_score = df.apply(momentum_score)

#1. absolute momentum
df_abs_momentum = df_momentum_score.aply(lambda x : np.where(x > 0, 1 , 0)) # 공매도 없이 롱만 취한다는 가정 하여 abs momentum > 0

# 2. relative momentum 
def rank_function(score, top_n = 3, ascending = True):

    rank = score.rank(axis = 1, method = 'max', ascending = ascending)

    selected_rank = rank.where(rank > len(stocks) - top_n, 0)
    return selected_rank

df_momentum_rank = rank_function(df_momentum_score).resample("1D").ffill()

#3. 변동성
def volatility_score(df, resample_by = 'D', interval : list = [20, 60, 126, 252]):

    annuity = {
        "D" : 252,
        "W" : 52,
        "M" : 12,
        "Y" : 1
    }
    dummy = list(reversed(interval))
    df_dummy = pd.DataFrame()

    for int in interval:
        df_dummy[f'vol_{int}'] = df.resample(resample_by) \
            .last() \
            .dropna(how = 'all') \
            .pct_change(1) \
            .rolling(int) \
            .std() \
            .dropna(how = 'all') \
            * np.sqrt(annuity.get(resample_by))
    res = df_dummy.mul(dummy, axis = 1)
    res = res.sum(axis = 1) / sum(interval)
    return res

df_vol_score = df.apply(volatility_score)
df_vol_rank = rank_function(df_vol_score, ascending = False)

#4. correlation score : sum of all the correl coefficient wrt other assets
def correlation_score(df, resample_by = 'D', interval : list = [20, 60, 126, 252]):

    ''' correl 은 각 list_month 별로 일자 / 종목 df 생성되므로 다른 계산 대비 한 차원 높음-> 계산하려면 n개의 list month 의 df를 모두 더해서 
    다시 산출 필요'''
    
    df_dummy = list()
    reversed_month = list(reversed(interval))

    for int in interval:
        multiplier = reversed_month[interval.index(int)]
        df_dummy.append(
            multiplier *  # 계산일수의 역수
            (df.resample(resample_by) \
            .last() \
            .dropna(how = 'all') \
            .pct_change(1) \
            .rolling(int) \
            .corr() \
            .dropna(how = 'all') \
            .sum(axis = 1) - 1) \
            .unstack(level = 1)
        )

    res = sum(df_dummy).dropna() / sum(interval)
    return res

df_correl_score = correlation_score(df)
df_correl_rank = rank_function(df_correl_score, ascending = False)

df_agg_rank = df_abs_momentum.multiply(df_momentum_rank) \
    + df_abs_momentum.multiply(df_vol_rank) \
    + df_abs_momentum.multiply(df_correl_rank)












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

def get_return(df):
    daily_ret = df['close'].pct_change(1) * df['trade']
    cumret = quant.df_cumret(daily_ret, is_ret = True)
    return cumret
    