from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import pandas as pd
import numpy as np
import quant

spy = openbb.stocks.load('SPY')

df = quant.ta(spy)

df = df.bollinger_band(days = 20, width = 2)

book = df.copy()
book['trade'] = 0

# backtesting : 
# vectorize 하면 안 됨 -> 매일마다 하루하루 포지션 쌓고 청산하는 모양새가 보여야 함 -> 오래걸려도 loop

# 간단한 볼린저 전략 : 상/하단 돌파시 매매 -> 중심선 도달시 매도

def trades(df, book):
    for i in df.index:
        # 1) upper bound exit
        if df.loc[i, 'close'] >= df.loc[i, 'bb_upper']:
            book.loc[i, 'trade'] = 1

        elif df.loc[i, 'close'] < df.loc[i, 'bb_upper'] and\
            df.loc[i, 'close'] > df.loc[i, 'bb_lower']:
            pass

        elif df.loc[i, 'close'] <=  df.loc[i, 'bb_upper']:
            book.ioc[i, 'trade'] = -1

        else:
            pass

    return book




        # 1-2) upper bound
        

