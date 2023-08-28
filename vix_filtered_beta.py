from openbb_terminal.sdk import openbb
import pandas as pd
import numpy as np
import quant

start_date = "2010-01-01"

usmv = openbb.stocks.load('usmv', start_date = start_date)
sphb = openbb.stocks.load('sphb', start_date = start_date)
vix = openbb.economy.index(["^VIX"], start_date = start_date).rename(columns = {'^VIX' : 'vix'})
spx = openbb.economy.index(["^SPX"], start_date = start_date).rename(columns = {'^SPX' : 'spx'})

usmv = quant.close_only(usmv).rename(columns = {'close': 'usmv'})
sphb = quant.close_only(sphb).rename(columns = {'close': 'sphb'})

## high vol condition

def hold_usmv(df_vix, vix_quantile = 0.8, interval = 252):
    '''logic : 
    1) 변동성 많이 높으면 -> 떨어질만큼 떨어졌으므로 되려 반등 노리고 high beta / 반대로 vix 일정 이하면 low beta 유지
    2) but VIX 꺾이는건 보고 들어가야... 안그러면 더 조질 수 있음 -> vix가 new high 일때는 low beta 유지
    => 아니면 VIX interval high 면 포지션 X?
    즉 양쪽 (vix 특정 수준 이하 / vix 아예 skyrocket) 일때는 low beta / vix 가 높지만 떨어지고 있는 특정 순간만 high beta'''

    # 1. vix is lower than n-th quantile
    cond_1 = df['vix'] < df['vix'].quantile(vix_quantile)

    #2. vix has spiked
    cond_2 = df['vix'] - df['vix'].rolling(interval).mean() > df['vix'].rolling(interval).std()

    res = np.where(cond_1 | cond_2, 1, 0)

    return res
    
df = pd.concat([usmv, sphb, vix], axis = 1, join = 'inner')

df['hold_usmv'] = hold_usmv(df.vix)
df['hold_sphb'] = np.where(df['hold_usmv'] == 1, 0, 1)
df['hold_usmv'] = df['hold_usmv'].shift(1) # 종가기준 매매하면 다음날 수익률부터 반영되게끔 하루 shift
df['hold_sphb'] = df['hold_sphb'].shift(1)

# # to expand :
# 1) VIX 최상위 0.9 에 있을때
# 2) VIX Term structure Invert 될때 포지션 안 잡는 걸로
# 3) Inversion but Vix drop 이면 매수


df[['usmv_ret', 'sphb_ret']] = df[['usmv', 'sphb']].pct_change(1)
df['usmv_ret'] = df['usmv_ret'] * df['hold_usmv']
df['sphb_ret'] = df['sphb_ret'] * df['hold_sphb']

df['total_ret'] = df['usmv_ret'] + df['sphb_ret']
df['total_cumret'] = quant.df_cumret(df.total_ret, is_ret = True)

# benchmark

spx = spx.loc[df.index].pct_change(1)
usmv = usmv.pct_change(1)
sphb = sphb.pct_change(1)
strat = df['total_ret']

ret = pd.concat([spx, usmv, sphb, strat], axis = 1, join = 'inner')
cumret = ret.apply(quant.df_cumret, is_ret = True)
cumret.plot()