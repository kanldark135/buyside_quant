import scipy.optimize as sciop
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
from openbb_terminal.sdk import openbb
import quant


#1. hands-on practice

#1) data collection for universe

start_date = '2010-01-01'
stocks = ['SPY', 'AAPL', 'MSFT', 'TLT', 'JPM', 'BAC', 'MRNA', 'META', 'WMT']


def df_stocks(tickers, start_date):
    
    df = pd.DataFrame()

    for i in tickers:
        a = openbb.stocks.load(i, start_date = start_date)
        df = pd.concat([df, a['Adj Close']], axis = 1)

    df.columns = stocks

    return df

df = df_stocks(stocks)

#2. params_annualized

df_ret = df.pct_change(1)
cov_matrix = df_ret.cov() * 252
weight_vectors = np.zeros(shape = len(stocks))
mean_ret = df.apply(quant.cagr)
std_ret = df_ret.std() * np.sqrt(252)
sharpe = mean_ret / std_ret


# global max_ret

def max_ret(df):

    df_ret = df.pct_change(1)
    cov_matrix = df_ret.cov() * 252
    mean_ret = df.apply(quant.cagr)
    stocks_count = len(mean_ret)
    weight_vectors = np.zeros(shape = stocks_count)

    def func_ret(weight_vectors, mean_ret):
        res = np.matmul(weight_vectors, mean_ret.values).sum()
        return - res
    
    def eqConstraint_1(x):
        a = np.ones(x.shape)
        b = 1
        res = np.matmul(a, x.T) - b
        return res
    
    bnd = [(0, 1) for i in stocks]
    constraint_1 = {'type' : 'eq', 'fun' : eqConstraint_1} # sum of all the weight equals to 1

    res = sciop.minimize(func_ret, weight_vectors, args = (mean_ret), bounds = bnd, constraints = [constraint_1])

    # results
    res_dict = dict(
            target_weight = res.x,
            target_return = -res.fun,
            target_vol = np.sqrt(np.matmul(np.matmul(res.x, cov_matrix), res.x.T))
            )

    return res_dict

# global min_var

def min_var(df):

    df_ret = df.pct_change(1)
    mean_ret = df.apply(quant.cagr)
    cov_matrix = df_ret.cov() * 252
    stocks_count = len(mean_ret)
    weight_vectors = np.zeros(stocks_count)

    def func_var(weight_vectors, cov_matrix):
        res = np.matmul(np.matmul(weight_vectors, cov_matrix), weight_vectors.T).sum()
        return res
    
    def eqConstraint_1(x):
        a = np.ones(x.shape)
        b = 1
        res = np.matmul(a, x.T) - b
        return res
    
    bnd = [(0, 1) for i in stocks]
    constraint_1 = {'type' : 'eq', 'fun' : eqConstraint_1} # sum of all the weight equals to 1

    res = sciop.minimize(func_var, weight_vectors, args = (cov_matrix), bounds = bnd, constraints = [constraint_1])
    
    # results
    res_dict = dict(
        target_weight = res.x,
        target_vol = np.sqrt(res.fun),
        target_return = np.matmul(res.x, mean_ret)
        )

    return res_dict

# minimize var while required minimum return constraint

def min_var_over_r(df, threshold_r):

    df_ret = df.pct_change(1)
    mean_ret = df.apply(quant.cagr)
    cov_matrix = df_ret.cov() * 252
    stocks_count = len(mean_ret)
    weight_vectors = np.zeros(stocks_count)

    def func_var(weight_vectors, cov_matrix):
        res = np.matmul(np.matmul(weight_vectors, cov_matrix), weight_vectors.T).sum()
        return res
    
    def eqConstraint_1(x):
        a = np.ones(x.shape)
        b = 1
        res = np.matmul(a, x.T) - b
        return res
    
    def ineqConstraint_1(x, mean_ret, threshold_r):
        a = mean_ret
        b = threshold_r
        res = np.matmul(a, x.T) - b
        return res
    
    bnd = [(0, 1) for i in stocks]
    constraint_1 = {'type' : 'eq', 'fun' : eqConstraint_1} # sum of all the weight equals to 1
    constraint_2 = {'type' : 'ineq', 'fun' : ineqConstraint_1, 'args' : (mean_ret, threshold_r)}

    res = sciop.minimize(func_var, weight_vectors, args = (cov_matrix), bounds = bnd, constraints = [constraint_1, constraint_2])

    res_dict = dict(
        target_weight = res.x,
        target_vol = np.sqrt(res.fun),
        target_return = np.matmul(res.x, mean_ret)
        )

    return res_dict

# efficient frontier -> optimal pf on each incremental change in vol

def efficient_frontier(df, increment):

    list_return = []
    list_vol = []
    list_weight = []

    low = min_var(df)['target_return']
    high = max_ret(df)['target_return']

    while low < high:
        res = min_var_over_r(df, low)
        list_return.append(res['target_return'])
        list_vol.append(res['target_vol'])
        list_weight.append(res['target_weight'])
        low += increment

    df = pd.DataFrame([list_return, list_vol])\
        .T\
        .rename(columns = {0 : 'return', 1: 'vol'})\
        .set_index(['vol'])
    
    return df