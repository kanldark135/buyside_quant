from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import quant
import util
import backtesting as bt
import pandas as pd
import numpy as np
from datetime import datetime as dt

df_stocks = pd.DataFrame()

start_date = '2010-01-01'
stocks = ['SPY', 'AAPL', 'MSFT', 'TLT', 'JPM', 'BAC', 'MRNA', 'META', 'WMT']
for i in stocks:

    df_raw = openbb.stocks.load(i, start_date = start_date)
    df = quant.close_only(df_raw, column_rename = i)
    df = util.extract_last_price(df)
    df_stocks = pd.concat([df_stocks, df], axis = 1)


# momentum_score 계산

def momentum(df, list_months : list = [1, 3, 6, 12]):

    ''' 일단 n-month 수익률로만 진행 '''
    df_dummy = pd.DataFrame()

    for i in list_months:
        df_dummy[f"ret_{i}"] = df.pct_change(i)

    dummy = list(reversed(list_months))
    res = df_dummy.loc[:, f'ret_{list_months[0]}': ].mul(dummy, axis = 1)

    res = res.sum(axis = 1) / sum(list_months)

    return res
    



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
    