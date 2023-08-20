import pandas as pd
import numpy as np

class measure:

    def __init__(self, df):

        try:
            self.df = df['Adj Close']
        except KeyError:
            try:
                potential_column_name = ['Close', "Price", "Last_Price"]
                self.df = df[df.columns.isin(potential_column_name)]

            except KeyError:

                if len(df.columns) == 1:
                    self.df = df
                else:
                    raise KeyError("Adj Close / Close / Last_Price 형태의 종가가 dataframe 에 존재하도록 하거나 그냥 종가 한줄 넣으세요")

        df.columns = ['close']

        self.ret = self.df.pct_change(1).iloc[1:]
        self.cumret = (self.ret + 1).cumprod()

    def cagr(self):
        ''' df is adj price'''
        cagr = self.cumret[-1] ** (252 / len(self.ret)) - 1
       
        return cagr
    
    def df_drawdown(self):
        drawdown = self.df/ self.df.expanding().max() - 1
        return drawdown

    def mdd(self):
        historical_max = self.df.cummax()
        drawdown_from_histmax = self.df / historical_max - 1
        mdd_rolling = drawdown_from_histmax.cummin()
        mdd = mdd_rolling.min()

        return mdd

    def annual_vol(self):
        vol = self.ret.std() * np.sqrt(252)
        
        return vol
        
    def sharpe(self):

        # monthly return based approach : following Morningstar Method

        monthly_ret = (self.ret + 1).resample("M").prod() - 1
        sharpe = monthly_ret.mean() / monthly_ret.std()
        return sharpe
    
    def calmar(self):

        res = self.cagr() / self.mdd()
        return res
    

class ta:

    def __init__(self, df):
        
        # ohlc 던 close only던 df_price feed 하면 종가만 튀어나오게 수정

        try:
            self.df = df['Adj Close']
        except KeyError:
            try:
                potential_column_name = ['Close', "Price", "Last_Price"]
                self.df = df[df.columns.isin(potential_column_name)]

            except KeyError:

                if len(df.columns) == 1:
                    self.df = df
                else:
                    raise KeyError("Adj Close / Close / Last_Price 형태의 종가가 dataframe 에 존재하도록 하거나 그냥 종가 한줄 넣으세요")
        
        df.columns = ['close']

        self.ret = self.df.pct_change(1).iloc[1:]
        self.cumret = (self.ret + 1).cumprod()


    def bollinger_band(self, days = 20, width = 2):

        df = self.df.to_frame()
        stdev = df.rolling(days).std()

        df = df.assign(center = df.rolling(days).mean(), bb_upper = df.rolling(days).mean().add(width * stdev), bb_lower = df.rolling(days).mean().sub(width * stdev))

        return df








        
