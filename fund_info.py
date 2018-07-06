import datetime
import time
import numpy as np
import pandas as pd
from CAL.PyCAL import *
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# 下面是定制参数
fundTicker = u"510300" #基金代码
beginDate = "2013-01-18" #历史行情起始日
endDate = "2018-07-05" #历史行情结束日


def get_tradeDates(beginDate="2018-01-01", endDate="2018-02-01"):
    """
    得到时间范围内的所有交易日期
    """
    df_dates = DataAPI.TradeCalGet(exchangeCD=u"XSHE",beginDate=beginDate,endDate=endDate,field=u"",pandas="1")
    list_tradeDates = df_dates[df_dates['isOpen']==1]['calendarDate'].tolist()
    return list_tradeDates

#得到某段时间内基金成份股的信息，主要得到持股数量


def get_fund_info(ticker='510300', beginDate="2018-01-01", endDate="2018-02-01"):
    list_fundInfo = []
    df_fundCons = DataAPI.FundETFConsGet(secID=u"",ticker=fundTicker,beginDate=beginDate,endDate=endDate,field=["secShortName", "ticker", "tradeDate", "consTicker", "consID", "consName", "quantity"],pandas="1")
    dates = get_tradeDates(beginDate, endDate)
    for day in dates:
        tmp_dict = {}
        try:
            if day.split("-")[2] == "01":
                # 每月1日打印下log，如果休市就跳过
                print("Deal to date: %s" % day)
            df_fundCons_oneDay = df_fundCons[df_fundCons["tradeDate"]==day]
            df_cons_info_oneDay = DataAPI.MktEqudGet(secID=u"",ticker=df_fundCons_oneDay["consTicker"].tolist(),tradeDate=day,beginDate=u"",endDate=u"",isOpen="",field=["ticker", "closePrice", "PB", "PE", "turnoverValue"],pandas="1")
            df =  pd.merge(df_fundCons_oneDay, df_cons_info_oneDay , left_on = 'consTicker', right_on = 'ticker')
            df["holdingValue"] = df["quantity"] * df["closePrice"]
            df['netAssetTotal'] = df['closePrice'] / df['PB'] * df['quantity']
            df['profitTotal'] = df['closePrice'] / df['PE'] * df['quantity']
            #df.to_csv("ttt.csv", encoding="GB18030")
            total_market_value = df['holdingValue'].sum()
            tmp_dict['fundTicker'] = df_fundCons_oneDay['ticker'].tolist()[0]
            tmp_dict['fundName'] = df_fundCons_oneDay['secShortName'].tolist()[0]
            tmp_dict['tradeDate'] = day
            tmp_dict['PB'] = df['holdingValue'].sum()/df['netAssetTotal'].sum()
            tmp_dict['PE'] = df['holdingValue'].sum()/df['profitTotal'].sum()
            tmp_dict['ROE'] = df['profitTotal'].sum()/df['netAssetTotal'].sum()
            tmp_dict['turnoverValue'] = df['turnoverValue'].sum()
            list_fundInfo.append(tmp_dict)
        except:
            print("在'%s'发生了错误" % day)
            pass
    return pd.DataFrame(list_fundInfo)
   

# 开始运算
df_fund = get_fund_info(fundTicker, beginDate, endDate)
# 开始生成报告
#df_fund.to_csv("FUND_%s_%s.csv" % (fundTicker, str(time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time())))), encoding="GB18030")

### 画图 ###
list_pb = df_fund['PB'].tolist()
list_pe = df_fund['PE'].tolist()
list_roe = df_fund['ROE'].tolist()
list_tradeDate = df_fund['tradeDate'].tolist()

# PB趋势图
fig, ax = plt.subplots(1,1)
fig.set_size_inches(35, 10)
xn = range(len(list_tradeDate))
ax.plot(xn, list_pb)
plt.xticks(xn, list_tradeDate)
# 设置x轴间隔，不要显示的太密集，间隔为40个交易日
visible_labels = [lab for lab in ax.get_xticklabels() if lab.get_visible() is True and lab.get_text() != '']
plt.setp(visible_labels, visible=False)
plt.setp(visible_labels[::40], visible=True)
plt.title('PB Trend')
plt.show()

# PE趋势图
fig, ax = plt.subplots(1,1)
fig.set_size_inches(35, 10)
xn = range(len(list_tradeDate))
ax.plot(xn, list_pe)
plt.xticks(xn, list_tradeDate)
# 设置x轴间隔，不要显示的太密集，间隔为40个交易日
visible_labels = [lab for lab in ax.get_xticklabels() if lab.get_visible() is True and lab.get_text() != '']
plt.setp(visible_labels, visible=False)
plt.setp(visible_labels[::40], visible=True)
plt.title('PE Trend')
plt.show()

# ROE趋势图
fig, ax = plt.subplots(1,1)
fig.set_size_inches(35, 10)
xn = range(len(list_tradeDate))
ax.plot(xn, list_roe)
plt.xticks(xn, list_tradeDate)
# 设置x轴间隔，不要显示的太密集，间隔为40个交易日
visible_labels = [lab for lab in ax.get_xticklabels() if lab.get_visible() is True and lab.get_text() != '']
plt.setp(visible_labels, visible=False)
plt.setp(visible_labels[::40], visible=True)
plt.title('ROE Trend')
plt.show()
