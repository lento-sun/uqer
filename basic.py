from CAL.PyCAL import *
import numpy as np
import datetime
import operator

today = datetime.date.today()
oneday = datetime.timedelta(days=1)

class Stock(object):
    def __init__(self):
        self.valueFunctions = { 'color': self.color_values, 
                                          'positions': self.positions_values,}
        
    def color_values(self):
        print "color"
        
    def positions_values(self):
        print "positions"
 
    def test(self, value='color'):
        self.valueFunctions['positions']()

def get_last_trade_date():
    """
    返回上一个交易日的日期，用浦发银行的信息做判断
    """
    i = 1
    while True:
        date = (today - oneday*i).strftime('%Y%m%d')
        if "empty" in str(DataAPI.MktStockFactorsOneDayGet(tradeDate=date,
                                                           secID='600000.XSHG',
                                                           field=['secID', 'PE'])).lower():
            i += 1
        else:
            return date
    
    
def csv2list(csv_data, header_len):
    list_data = str(csv_data).split()
    # 如果股票信息以"Empty"开头，表示该股票在当日处于非交易状态或者已经退市
    if str(list_data[0]).startswith("Empty"):
        return None
    # 去除title字段以及序列号
    for i in range(header_len + 1):
        list_data.pop(0)
    return list_data

def find_common(list1, list2):
    # 找到两个list里面的相同股票代码
    common_list = []
    for item1 in list1:
        for item2 in list2:
            if item1[0] == item2[0]:
                common_list.append(item1[0])
    return common_list
    
def get_all_stocks(market='SH', watch_keys=['secID', 'PE', 'PVT'], date=yesterday, sortby='secID', reverse_sort=False):
    """
    :param market: 表示选择哪个交易所的股票
    :param watch_keys: 表示获取哪些信息
    :param date: 表示获取哪天的信息
    :param sortby: 根据哪个信息来排序股票列表
    :param reverse_sort: 是否倒序排列
    :return: 股票的字典列表
    """
    stock_code_list = []
    stock_dict = {}
    stocks_list = []
    not_float_value = ['secID'] # 如果一个factor不是数字，则转换为str，否则转换为float
    if market == 'SH':
        postfix = ".XSHG"
        start_code = 600000
        end_code = 604000
    elif market == "SZ":
        postfix = ".XSHE"
        start_code = 0
        end_code = 4000
    elif market == "CY":
        postfix = ".XSHE"
        start_code = 300000
        end_code = 302000
    else:
        print("你输入了错误的交易所信息，交易所有SH/SZ/CY")
        return
    for i in range(start_code, end_code):
        stock_code = str(i).zfill(6) + postfix
        stock_code_list.append(stock_code)
    for stock_code in stock_code_list:  
        try:
            stock_dict = {}
            csv_data = DataAPI.MktStockFactorsOneDayGet(tradeDate=date, secID=stock_code, field=watch_keys)
            cur_stock = csv2list(csv_data, len(watch_keys))
            if cur_stock:
                if len(cur_stock) != len(watch_keys):
                    print("股票" + stock_code + "可能有问题，请检查")
                for i in range(len(watch_keys)):
                    if watch_keys[i] in not_float_value:
                        stock_dict[watch_keys[i]] = str(cur_stock[i])
                    else:
                        stock_dict[watch_keys[i]] = float(cur_stock[i])
                stocks_list.append(stock_dict)
        except:
            pass # 股票代码不存在等异常不做处理，直接跳过
    return sorted(stocks_list, key = operator.itemgetter(sortby), reverse=reverse_sort)


if __name__ == "__main__":
    stock_list = get_all_stocks(date=get_last_trade_date(), sortby="PE")
    print stock_list


