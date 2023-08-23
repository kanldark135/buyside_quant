import pandas as pd
import numpy as np


def sort(df):

    try:
        df = df['Adj Close']
    except KeyError:
        try:
            potential_column_name = ['Close', "Price", "Last_Price"]
            df = df[df.columns.isin(potential_column_name)]

        except KeyError:

            if len(df.columns) == 1:
                df = df
            else:
                raise KeyError("Adj Close / Close / Last_Price 형태의 종가가 dataframe 에 존재하도록 하거나 그냥 종가 한줄 넣으세요")
    
    df.columns = ['close']
    return df

def df_cumret(df):
    ret = df.pct_change(1).iloc[1:]
    cumret = (ret + 1).cumprod()
    return cumret

def cagr(df):
    ''' df is adj price, annualize by 252 days'''
    ret = df.pct_change(1).iloc[1:]
    cumret = (ret + 1).cumprod()
    cagr = cumret[-1] ** (252 / len(ret)) - 1
    return cagr

def df_drawdown(df):
    drawdown = df/ df.cummax() - 1
    return drawdown

def mdd(df):
    drawdown = df / df.cummax() - 1
    mdd_rolling = drawdown.cummin()
    mdd = mdd_rolling.min()
    return mdd

def annual_vol(df):
    ret = df.pct_change(1).iloc[1:]
    vol = ret.std() * np.sqrt(252)
    return vol
    
def sharpe(df):
    ''' monthly arithmetic return / monthly stdev -> : following Morningstar Method '''
    ret = df.pct_change(1).iloc[1:]
    monthly_ret = (ret + 1).resample("M").prod() - 1
    sharpe = monthly_ret.mean() / monthly_ret.std()
    return sharpe

def calmar(df):
    res = cagr(df) / mdd(df)
    return res
    



class ta:

    def __init__(self, df):
        
        # ohlc 던 close only던 df_price feed 하면 종가만 튀어나오게 수정

        self.df = sort(df)
        self.ret = self.df.pct_change(1).iloc[1:]
        self.cumret = (self.ret + 1).cumprod()

    def bollinger_band(self, days = 20, width = 2):

        df = self.df.to_frame()
        stdev = df.rolling(days).std()

        df = df.assign(bb_center = df.rolling(days).mean(), bb_upper = df.rolling(days).mean().add(width * stdev), bb_lower = df.rolling(days).mean().sub(width * stdev))

        return df








        
