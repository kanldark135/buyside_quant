from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import pandas as pd
import numpy as np
import quant

spy = openbb.stocks.load('SPY')

df = quant.ta.bollinger_band(days = 20, width = 2)

book = df.copy()

def trading(df, book):

    # short entry : stock > bb_upper