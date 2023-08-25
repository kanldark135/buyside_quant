from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import quant
import util
import pandas as pd
import numpy as np
from datetime import datetime as dt


start_date = '2010-01-01'
stocks = ['SPY', 'AAPL', 'MSFT', 'TLT', 'JPM', 'BAC', 'MRNA', 'META', 'WMT']
for i in stocks:

    df_raw = openbb.stocks.load(i, start_date = start_date)
    df = quant.close_only(df_raw)
    
df = util.extract_last_price(df)


# momentum 계산

def calc_momentum(df, list_months : list = [1, 3, 6, 12]):

    ''' 일단 n-month 수익률로만 진행 '''

    for i in list_months:
        df[f"ret_{i}"] = df['close'].pct_change(i)

    dummy = list(reversed(list_months))
    res = df.loc[:, f'ret_{list_months[0]}': ].mul(dummy, axis = 1)

    df['momentum_score'] = res.sum(axis = 1) / sum(list_months)

    # absolute momentum

    df = df.assign(abs_momentum = np.where(df.momentum_score > 0, 1, 0))
    
    return df


df['trade'] = 0

def put_trade(df):
    prev_position = df.shift(1)
    if prev_position != 0:
        if df.abs_momentum == 1:
            df['trade'] == 1
