#%%

from openbb_terminal.sdk import openbb
import os
from dotenv import load_dotenv

import pandas as pd
import numpy as np

load_dotenv()

email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
token = os.environ.get('OPENBB_TOKEN')

openbb.login(email, password, token)

# # set apikey to certain api provider
openbb.keys.alphavantage("RZNGCMVQ77C1RPF2", persist = True)
# openbb.keys.finnhub("cj6g7nhr01ql0ntir2s0cj6g7nhr01ql0ntir2sg", persist = True)


#%%

res = openbb.stocks.screener.screener_data('new_high')
tickers = r