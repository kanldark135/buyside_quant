import pandas as pd
import numpy as np


def close_only(df, column_rename = 'close'):
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
    
    df = df.to_frame()
    df.columns = [column_rename]
    return df

def df_cumret(df, is_ret = False):
    ''' df 는 종가거나 여타 가격이어야만 함 / df가 수익률인 경우 is_ret = True로 표기'''
    if is_ret == True:
        cumret = (df + 1).cumprod() - 1
    else:
        ret = df.pct_change(1).iloc[1:]
        cumret = (ret + 1).cumprod() - 1
    return cumret

def cagr(df, is_ret = False):
    ''' df 는 종가거나 여타 가격이어야만 함 / df가 수익률인 경우 is_ret = True로 표기.
    CAGR 은 일수익률 -> 252일화'''
    if is_ret == True:
        cumret = (df + 1).cumprod()
        cagr = cumret[-1] ** (252 / len(df)) - 1
    else:
        ret = df.pct_change(1).iloc[1:]
        cumret = (ret + 1).cumprod()
        cagr = cumret[-1] ** (252 / len(ret)) - 1
    return cagr

def df_drawdown(df, is_ret = False):
    ''' df 는 종가거나 여타 가격이어야만 함 / df가 수익률인 경우 is_ret = True로 표기'''
    if is_ret == True:
        cumret = (df + 1).cumprod()
        drawdown = cumret / cumret.cummax() - 1
    else:
        drawdown = df/ df.cummax() - 1
    return drawdown

def mdd(df, is_ret = False):
    ''' df 는 종가거나 여타 가격이어야만 함 / df가 수익률인 경우 is_ret = True로 표기'''
    if is_ret == True:
        cumret = (df + 1).cumprod()
        drawdown = cumret / cumret.cummax() - 1
    else:
        drawdown = df / df.cummax() - 1
    
    mdd_rolling = drawdown.cummin()
    mdd = mdd_rolling.min()
    return mdd

def annual_vol(df, is_ret = False):
    ''' df 는 종가거나 여타 가격이어야만 함 / df가 수익률인 경우 is_ret = True로 표기'''
    if is_ret == True:
        vol = df.std() * np.sqrt(252)
    else:
        ret = df.pct_change(1).iloc[1:]
        vol = ret.std() * np.sqrt(252)
    return vol
    
def sharpe(df, rf = 0, is_ret = False):
    ''' df 는 종가거나 여타 가격이어야만 함 / df가 수익률인 경우 is_ret = True로 표기.
    Morningstar 방법론 적용 (CAGR 가 아니라 월 초과수익률들의 산술평균 / 월 초과수익률들의 월변동성) 으로 계산monthly arithmetic return / monthly stdev -> : following Morningstar Method
    https://awgmain.morningstar.com/webhelp/glossary_definitions/mutual_fund/mfglossary_Sharpe_Ratio.html'''
    
    rf = rf / 12
    
    if is_ret == True:
        monthly_ret = ((df + 1).resample("M").prod() - rf) -   1
        mu = monthly_ret.mean() # CAGR 가 아니라 단순 산술평균
        std = np.sqrt((monthly_ret - mu - rf).pipe(np.power, 2).sum() / (len(monthly_ret) - 1))
        sharpe = mu / std     
    else:
        ret = df.pct_change(1).iloc[1:]
        monthly_ret = ((ret + 1).resample("M").prod() - rf) -   1
        mu = monthly_ret.mean() # CAGR 가 아니라 단순 산술평균
        std = np.sqrt((monthly_ret - mu - rf).pipe(np.power, 2).sum() / (len(monthly_ret) - 1))
        sharpe = mu / std 

    return sharpe

def calmar(df : pd.Series, is_ret = False):
    res = cagr(df, is_ret = is_ret) / mdd(df, is_ret = is_ret)
    return -res
    



class ta:

    def __init__(self, df):
        
        # ohlc 던 close only던 df_price feed 하면 종가만 튀어나오게 수정

        self.df = close_only(df)
        self.ret = self.df.pct_change(1).iloc[1:]
        self.cumret = (self.ret + 1).cumprod()

    def bollinger_band(self, days = 20, width = 2):

        df = self.df
        stdev = df.rolling(days).std()
        df = df.assign(bb_center = df.rolling(days).mean(), bb_upper = df.rolling(days).mean().add(width * stdev), bb_lower = df.rolling(days).mean().sub(width * stdev))

        return df








        
