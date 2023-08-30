import pandas as pd
import numpy as np
from openbb_terminal.sdk import openbb
import quant


def load_stocks(tickers : list, start_date = "1909-01-01", end_date = "2099-01-01"):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df = pd.DataFrame()

    for i in tickers:

        df_raw = openbb.stocks.load(i, start_date = start_date)
        temp = quant.close_only(df_raw, column_rename = i)
        df = pd.concat([df, temp], axis = 1)
        df = df.dropna()
    
    return df

def extract_last_price(df, interval = "M"):

    '''df.index 가 datetime 형태여야만 함. interval 은 resample by 그대로 따라감'''
    
    # 1. year - month 별로 그룹핑된 groupby object 생성
    grouped = df.resample(interval)
    
    # 2. last day 뽑아내는 함수 및 적용
    def extract_last_day(grouped):
        if not grouped.empty:
            return grouped.iloc[[-1]].index

        # downsampling 하게되면 index[-1] 사용
    
    # 3. 원래 가격 df 에서 마지막 날만 reindex로 filtering. df.filter(items = last_days, axis = 0 도 동일)
    last_days = grouped.apply(extract_last_day).dropna().values
    df_reindexed = df.reindex(last_days)

    return df_reindexed


def extract_first_price(df, interval = "M"):

    '''df.index 가 datetime 형태여야만 함. interval 은 resample by 그대로 따라감'''
    
    # 1. year - month 별로 그룹핑된 groupby object 생성
    grouped = df.resample(interval)
    
    # 2. last day 뽑아내는 함수 및 적용
    def extract_first_day(grouped):
        if not grouped.empty:
            return grouped.iloc[[-1]].index

        # downsampling 하게되면 index[-1] 사용
    
    # 3. 원래 가격 df 에서 마지막 날만 reindex로 filtering. df.filter(items = last_days, axis = 0 도 동일)
    first_days = grouped.apply(extract_first_day).dropna().values
    df_reindexed = df.reindex(first_days)

    return df_reindexed