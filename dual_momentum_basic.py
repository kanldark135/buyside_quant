from openbb_terminal.sdk import openbb
import FinanceDataReader as fdr

import quant
import util
import pandas as pd
import numpy as np
from datetime import datetime as dt

df = openbb.stocks.load('SPY', start_date = '2010-03-20')
df = quant.close_only(df)
df = util.extract_last_price(df)


# momentum 계산
#
#  