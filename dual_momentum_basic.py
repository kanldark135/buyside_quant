from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import pandas as pd
import numpy as np
from datetime import datetime as dt

df = openbb.stocks.load('SPY', start_date = '2010-3-20')

df_monthly = df.resample("")

def check_last_day(x):
    dt.month


