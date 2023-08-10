class performance:

    def __init__(self, df):

        try:
            df.columns['Adj Close']
        except TypeError:
            if df.columns.isin['Close', 'last_Price'].any(1):
                