import numpy as np
import pandas as pd
import FinanceDataReader as fdr
import seaborn as sn
from openbb_terminal.sdk import openbb
import datetime as dt

import matplotlib.pyplot as plt
import statsmodels.api as sm

## recession

start_date = '1970-01-01'
end_date = '2023-08-01'



# # 1 > time series model - markov regression 

sp500 = openbb.economy.index(["^SPX"])
ret_sp500 = sp500.pct_change(1).dropna()

model_plain = sm.tsa.MarkovRegression(ret_sp500, k_regimes = 2, trend = 'c', switching_variance= True)
res = model_plain.fit()   

prob_plain = res.smoothed_marginal_probabilities[0]

model_ar4 = sm.tsa.MarkovAutoregression(ret_sp500, k_regimes = 2, trend = 'c', order = 4, switching_variance= True)
res = model_ar4.fit()   

prob_ar4 = res.smoothed_marginal_probabilities[0]

#2. feature based model

#3. ML based model (not so diff from 2)