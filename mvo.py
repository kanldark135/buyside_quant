import scipy.optimize as sciop
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
from openbb_terminal.sdk import openbb
import quant


#1. hands-on practice

#1) data collection for universe

start_date = '2010-01-01'
stocks = ['AAPL', 'MSFT', 'TLT', 'JPM', 'BAC', 'MRNA', 'META', 'WMT']

df = pd.DataFrame()

for i in stocks:
    a = openbb.stocks.load(i, start_date = start_date)
    df = pd.concat([df, a['Adj Close']], axis = 1)

df.columns = stocks
df_ret = df.pct_change(1)

#2. params_annualized

cov_matrix = df_ret.cov() * 252
weight_vectors = np.zeros(shape = len(stocks)) 
mean_ret = df_ret.mean() * 252
std_ret = df_ret.std() * np.sqrt(252)
sharpe = mean_ret / std_ret


def min_var(weight_vector, cov_matrix):
    res = np.matmul(np.matmul(weight_vector, cov_matrix), weight_vector.T).sum()
    return res

def max_ret(weight_vector, mean_ret):
    res = np.matmul(weight_vector, mean_ret.values).sum()
    return res

def balance_btwn(weight_vector, cov_matrix, bnd_ret):
    pass


sciop.minimize(min_var, weight_vectors, args = (cov_matrix), bounds = [(0, 1) for x in stocks], constraints = {'type' : 'eq', 'fun' : lambda x : sum(x) - 1})


