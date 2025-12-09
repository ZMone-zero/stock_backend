# -*- coding: utf-8 -*-
from stock_data_query import StockQuery

def sample():
    #使用示例
    
    # 数据库配置
    db_config = {
        'host': 'mysql-10fed60c-project-manonghezuoshe.g.aivencloud.com',      # 我们要用的MySQL主机地址
        'port': 23966,            # 我们要用的MySQL端口
        'user': 'avnadmin', # 我们要用的用户名
        'password': '', # 我们要用的密码（小组内部保密）
        'database': 'defaultdb'   # 我们要用的数据库名
    }
    
    # 创建分页查询器
    query = StockQuery(**db_config)
    
    try:
        # 示例: 获取第1页数据并输出获取的数据
        test_page_number=1
        print(f"获取第 {test_page_number} 页股票数据...")
        page_1_data = query.get_stocks_by_page_number(test_page_number)
        print(f"获取到 {len(page_1_data)} 条记录")
        for i, stock in enumerate(page_1_data, 1):
            print(f"记录 {i}/{len(page_1_data)}:")
            print(f"  ID: {stock['id']}")
            print(f"  股票唯一代码: {stock['ts_code']} ")
            print(f"  股票代码: {stock['symbol']}")
            print(f"  名称: {stock['name']}")
            print(f"  地域: {stock.get('area', 'N/A')}")
            print(f"  行业: {stock.get('industry', 'N/A')}")
            print(f"  上市日期: {stock.get('list_date', 'N/A')}")
            print("-" * 40)
        #示例：获取股票代码（symbol)为1的股票数据
        test_symbol = "1"
        stock_info = query.get_stock_by_symbol(test_symbol)
        if stock_info:
            print(f"\n找到股票 {test_symbol} :")
            print(f"  股票全码: {stock_info.get('ts_code')}")
            print(f"  股票名称: {stock_info.get('name')}")
            print(f"  所属行业: {stock_info.get('industry')}")
            print(f"  上市日期: {stock_info.get('list_date')}")
        else:
            print(f"\n未找到股票代码为 {test_symbol} 的记录")
        #示例：获取股票名称为a的股票数据
        test_name = "a"
        stock_info = query.get_stock_by_name(test_name)
        if stock_info:
            print(f"\n找到股票 {test_name}:")
            print(f"  股票全码: {stock_info.get('ts_code')}")
            print(f"  股票名称: {stock_info.get('name')}")
            print(f"  所属行业: {stock_info.get('industry')}")
            print(f"  上市日期: {stock_info.get('list_date')}")
        else:
            print(f"\n未找到股票代码为 {test_name} 的记录")
        # 示例: 获取第1页a地域的股票数据并输出获取的数据
        test_area = "a"
        print(f"获取第1页 {test_area} 地域的股票数据...")
        page_1_data = query.get_stocks_by_page_and_area(1,test_area)
        print(f"\n获取到 {test_area} 地域的 {len(page_1_data)} 条记录")
        for i, stock in enumerate(page_1_data, 1):
            print(f"记录 {i}/{len(page_1_data)}:")
            print(f" ID: {stock['id']}")
            print(f" 股票唯一代码: {stock['ts_code']} ")
            print(f" 股票代码: {stock['symbol']}")
            print(f" 名称: {stock['name']}")
            print(f" 地域: {stock.get('area', 'N/A')}")
            print(f" 行业: {stock.get('industry', 'N/A')}")
            print(f" 上市日期: {stock.get('list_date', 'N/A')}")
            print("-" * 40)
        # 示例: 获取第1页a行业的股票数据并输出获取的数据
        test_industry = "a"
        print(f"获取第1页 {test_industry} 行业的股票数据...")
        page_1_data = query.get_stocks_by_page_and_industry(1,test_industry)
        print(f"获取到 {test_industry} 行业的 {len(page_1_data)} 条记录")
        for i, stock in enumerate(page_1_data, 1):
            print(f"记录 {i}/{len(page_1_data)}:")
            print(f"  ID: {stock['id']}")
            print(f"  股票唯一代码: {stock['ts_code']} ")
            print(f"  股票代码: {stock['symbol']}")
            print(f"  名称: {stock['name']}")
            print(f"  地域: {stock.get('area', 'N/A')}")
            print(f"  行业: {stock.get('industry', 'N/A')}")
            print(f"  上市日期: {stock.get('list_date', 'N/A')}")
            print("-" * 40)
        #示例: 获取股票000001.SZ最近7天日线数据
        test_ts_code_1="000001.SZ"
        data_7_days = query.get_recent_7_days_data(test_ts_code_1)
        print(f"\n今天是{data_7_days[6]['trade_date']}")
        print(f"{test_ts_code_1}最近7天数据:")
        for i, day_data in enumerate(data_7_days, 1):
            print(f"{i}. {day_data['trade_date']}： ")
            print(f"开盘价：{day_data['open']}")
            print(f"收盘价：{day_data['close']}")
            print(f"最高价：{day_data['high']}")
            print(f"最低价：{day_data['low']}")
            print(f"成交量：{day_data['vol']}")
            print(f"成交额：{day_data['amount']}")
            print("-" * 40)
        #示例: 获取股票000001.SZ最新技术指标
        test_ts_code_2="000001.SZ"
        tech_data = query.get_latest_technical_indicators(test_ts_code_2)
        if tech_data['trade_date']:
            print(f"\n找到股票{test_ts_code_2}的最新技术指标:")
            print(f"id: {tech_data['id']}")
            print(f"最新数据日期: {tech_data['trade_date']}")
            print(f"MA5：{tech_data['ma5']}")
            print(f"MA20：{tech_data['ma20']}")
            print(f"RSI：{tech_data['rsi']}")
            print(f"MACD：{tech_data['macd']}")
            print(f"布林线上轨：{tech_data['boll_upper']}")
            print(f"布林线下轨：{tech_data['boll_lower']}")
        else:
            print("未找到数据")
        # 示例1: 查询存在当天预测数据的股票
        test_ts_code_3="000001.SZ"
        predict = query.get_today_predictions_by_ts_code(test_ts_code_3)
        print(f"股票 {test_ts_code_3} 当天预测数据:")
        for pred in predict:
            print(f"ID: {pred['id']}")
            print(f"预测日期: {pred['predict_date']}")
            print(f"目标日期: {pred['for_date']}")
            print(f"预测分数: {pred['prediction_score']}")
            
    except Exception as e:
        print(f"程序执行错误: {e}")


    

if __name__ == "__main__":
    sample()



