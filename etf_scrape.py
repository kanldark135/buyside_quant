from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# 1) chromedriver 이슈

# chromedriver 가 시도때도없이 업데이트되므로 그때마다 받기 귀찮으므로 아예 실행할때마다 재설치
# pip install webdriver_manager 설치 필요
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 2) driver 선언하기 driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()))

service = ChromeService()
driver = webdriver.Chrome(service = service)


page = 0

df_origin = pd.DataFrame()

while True:

    url = f"https://etfdb.com/etfs/asset-class/bond/#etfs&sort_name=price&sort_order=asc&page=1"
    driver.get(url)
    table = driver.find_element(By.CSS_SELECTOR, "table#etfs")
    df_dummy = pd.read_html(table.get_attribute('outerHTML'))[0]
    df_origin = pd.concat([df_origin, df_dummy], axis = 0)

    next_button = driver.find_element(By.CSS_SELECTOR, "div#featured-wrapper > div.col-md-8 > div.table-content > div.social-module-target > div.mm-super-content-centers-tabs.panel.panel-default.table-module.table-module-shareable.table-tabs > div.bootstrap-table > div.fixed-table-container > div.fixed-table-pagination > div.pull-center.pagination > ul > li.page-next > a")

    next_button.click()
    
    time.sleep(6)


# cleansing

df = df_origin.set_index('Symbol')

df = df.loc[~df.index.isin(df.filter(like = "Click Here", axis = 0).index)] # 이상한 텍스트 로우 제거

def column_names(i):
    array = np.array(i.split(" "))
    unique_array = np.unique(array)

    text = " ".join(list(unique_array))
    return text

df.columns = list(map(column_names, df.columns)) # 컬럼명 중복현상 제거

df.dropna(how = 'any', subset = ['($MM) Assets Total', 'Closing Previous Price'], inplace = True) # 필터링 기준 값 없는거 제거

from decimal import Decimal
import re

def float_only(txt):
    value = Decimal(re.sub(r'[^\d.]', "", txt))
    return value

df.update(df[['($MM) Assets Total', 'Closing Previous Price']].applymap(float_only))
df.sort_values(['Closing Previous Price'], inplace = True)