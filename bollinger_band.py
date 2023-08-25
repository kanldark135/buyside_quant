from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import pandas as pd
import numpy as np
import quant

spy = openbb.stocks.load('SPY', start_date = '2010-01-01')
ta = quant.ta(spy)

df = ta.bollinger_band(days = 20, width = 2)
df.dropna(inplace = True)
df['trade'] = 0

# backtesting : 
# vectorize 하면 안 됨 -> 매일마다 하루하루 포지션 쌓고 청산하는 모양새가 보여야 함 -> 오래걸려도 loop

# 간단한 볼린저 전략 : 상/하단 돌파시 역방향 매매 -> 중심선 도달시 청산 

def put_trade(df, lagging = 1):
    df_prev = df.shift(lagging)
    for i in df.index:
        prev_position = df.shift(1).loc[i, 'trade']
        # 만약 기존 포지션 있으면
        if prev_position != 0:
            if np.sign(df_prev.loc[i, 'close'] - df_prev.loc[i, 'bb_center']) != \
                np.sign(df.loc[i, 'close'] - df.loc[i, 'bb_center']):
                df.loc[i, 'trade'] = 0  # 만약 전기간 중심선 못 넘었는데 오늘 넘으면 전일까지 포지션 청산
            else:
                df.loc[i, 'trade'] = prev_position
        # 만약 기존 포지션 없으면
        elif prev_position == 0:
            if df.loc[i, 'close'] >= df.loc[i, 'bb_upper']:
                df.loc[i, 'trade'] = -1
            elif df.loc[i, 'close'] <= df.loc[i, 'bb_lower']:
                df.loc[i, 'trade'] = 1
            else:
                df.loc[i, 'trade'] = prev_position

    # 시그널 나면 종가에 매매하는 느낌이므로 실제 포지션 홀딩은 다음날부터 : trade -> trade.shift(1) 해야함
    df['trade'] = df['trade'].shift(1)

    return df

res = put_trade(df)

def get_return(df):
    daily_ret = df['close'].pct_change(1) * df['trade']
    cumret = (daily_ret + 1).cumprod() - 1
    return dict(daily = daily_ret, cum = cumret)
    
sharpe = quant.sharpe()