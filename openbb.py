import numpy as np
import pandas as pd
import FinanceDataReader as fdr
import seaborn as sn
from openbb_terminal.sdk import openbb

openbb.stocks.options.chains('AAPL')

treasury = openbb.fixedincome.treasury()