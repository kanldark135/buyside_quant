import yfinance as yf
import pandas_datareader as pdr
import pandas_ta as ta
import pandas as pd
import numpy as np
import os
from datetime import datetime as dt
from dotenv import load_dotenv

#1. data procurement

def get_price(tickers, start_date, end_date, resample = "D"):
    start_date = pd.to_datetime(start_date) - pd.DateOffset(years = 1)
    data = yf.download(tickers, start = start_date, end = end_date)
    data = data[['Adj Close']]
    data = data.resample(resample).last()
    data = data.ffill()
    return data

# compute momentum
@pd.api.extensions.register_dataframe_accessor('momentum')
class compute_momentum:

    '''self -> df_price'''

    def __init__(self, df_price):
        self.df = df_price

    def wma(self, lookback_period, weight = None):

        if weight == None:
            weight = np.arange(1, lookback_period + 1)

        '''momentum score = 오늘 주가 / 시간weight 만큼 가중평균한 값 - 1'''
        wma = self.df.rolling(window = lookback_period).apply(lambda x : sum(x.multiply(weight, axis = 0)) / sum(weight))
        rel_mom = self.df / wma - 1

        def abs_score(x):
            if x >= 0:
                return 1
            elif x < 0:
                return -1
        abs_mom = rel_mom.map(lambda x : abs_score(x))

        return {'rel' : rel_mom, 'abs' : abs_mom}
    

''' 향후 전략들은 전략.py 만들어서 별도의 모듈로 옮기기'''

def PAA(ticker_risk, ticker_safe, start_date, end_date, resample, lookback_period, protection_factor = 1, risky_limit = 6):
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # 1. 가격데이터 procurement

    daily_risk = get_price(ticker_risk, start_date, end_date, resample = "D")
    daily_risk.columns = ticker_risk
    daily_safe = get_price(ticker_safe, start_date, end_date, resample = "D")
    daily_safe.columns = ticker_safe
    
    price = pd.concat([daily_risk, daily_safe], axis = 1)

    df_risk = daily_risk.resample(resample).last().dropna()
    df_safe = daily_safe.resample(resample).last().dropna()

    # 2. 모멘텀 df 계산
    
    wma = df_risk.momentum.wma(lookback_period)
    df_rel = wma['rel'].dropna()
    df_abs = wma['abs'].dropna()

    # 3. 모멘텀 지표를 기반으로 비율 계산

    def compute_PAA_weight():

        risky_bool = df_abs.eq(1)
        n_of_good = np.minimum(risky_bool.sum(axis = 1), risky_limit)
        df_rank = df_rel.rank(axis = 1, ascending = False)
        risky_bool = df_rank.le(n_of_good, axis = 0)

        def bond_weight(x, protection_factor):
            N = df_risk.shape[1]
            res = np.minimum((N - x) / (N - (protection_factor * N / 4)), 1.00) # protection factor 0 ~ 1 사이
            return res

        bond_fraction = n_of_good.apply(bond_weight, protection_factor = protection_factor)
        risky_fraction = 1 - bond_fraction
        risky_weight = (risky_fraction / n_of_good)

        def apply_weight(row, risky_weight):
            res = row.replace(True, risky_weight[row.name])
            return res

        weight = risky_bool.apply(lambda x : apply_weight(x, risky_weight), axis = 1)
        weight = weight.replace(False, 0)
        weight[ticker_safe[0]] = bond_fraction

        return weight
    
    df_weight = compute_PAA_weight()

    def compute_daily_return():

        df_daily_weight = df_weight.resample("D").ffill().shift(1).dropna()
        df_daily_ret = price.pct_change(1)

        # 1) 일수익률 날짜랑 일치 + weight는 ffill 적용 + 산출일 다음날 매매하므로 하루씩 push
        # 산출일 다음날 하는 매매도 사실 100%는 맞지 않는게 
        # 산출일 다음날 (=리밸런싱일) 시초가부터 gap 변동폭이 그날 수익률의 대부분을 차지하는 경우
        # 해당 일의 수익 대부분도 어짜피 전일 비중으로 투자한 것과 동일할 가능성 높음
        # 이런 부분 매매비용과 합산해서 다 슬리피지로 퉁 쳐서 생각

        res = df_daily_weight.multiply(df_daily_ret).dropna()
        return res
    
    df_return = compute_daily_return()
    
    return df_weight, df_return

if __name__ == "__main__":
    
    ticker_risk = ['SPY','QQQ','IWM','VGK','EWJ','EEM','IYR','GSG','GLD','HYG','LQD','TLT'] # to env
    ticker_safe = ['IEF']
    start_date = '19910101'
    end_date = dt.today()
    resample_period = "M"
    lookback_period = 12
    protection_factor = 2
    risky_limit = 6

    weight, ret = PAA(ticker_risk, ticker_safe, start_date, end_date, resample_period, lookback_period, protection_factor, risky_limit)