import pandas as pd
import json
import datetime
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from urllib.parse import unquote
import math

from services.gemini_service import GeminiService
from services.news_service import NewsService

gemini_service = GeminiService()
news_service = NewsService()

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
# 全局变量，存储股票代码到名称的映射
stock_symbols_to_name = {}


# 载入台湾股票分类数据
def load_tw_stock_categories():
    try:
        with open('tw_stock_categories.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"载入台湾股票分类数据失败: {str(e)}")
        return {"categories": []}


# 载入台湾上市股票数据
def load_twse_listed_stocks():
    try:
        # 读取CSV文件
        df = pd.read_csv('twse_listed_stocks.csv')
        # 转换为字典列表
        stocks = df.to_dict('records')
        # 建立映射
        for stock in stocks:
            stock_symbols_to_name[str(stock['有價證券代號'])] = stock['有價證券名稱']
        return stocks
    except Exception as e:
        print(f"载入台湾上市股票数据失败: {str(e)}")
        return []


# 载入美国股票分类数据
def load_us_stock_categories():
    try:
        with open('us_stock_categories.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 建立美股代码到公司名称的映射
        for stock in data:
            stock_symbols_to_name[stock['ticker']] = stock['name']
        return data
    except Exception as e:
        print(f"载入美国股票分类数据失败: {str(e)}")
        return []


# 载入美国股票列表
def load_us_stock_list():
    try:
        # 读取CSV文件
        df = pd.read_csv('us_stock_list.csv')
        # 转换为字典列表
        stocks = df.to_dict('records')
        # 建立映射
        for stock in stocks:
            stock_symbols_to_name[stock['Symbol']] = stock['English name']
        return stocks
    except Exception as e:
        print(f"载入美国股票列表失败: {str(e)}")
        return []


# 初始化函数，取代 before_first_request
def initialize_data():
    with app.app_context():
        load_twse_listed_stocks()
        load_us_stock_categories()
        load_us_stock_list()
        print(f"已载入 {len(stock_symbols_to_name)} 个股票代码到名称的映射")


# 获取股票数据接口
@app.route('/api/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        symbol_name = unquote(symbol)

        # 模拟股价数据 - 生成过去30天的数据
        mock_data = []
        current_date = datetime.datetime.now()

        # 设置起始价格 - 可以根据股票代码生成一个伪随机的起始价格
        try:
            base_price = int(int(symbol_name) % 1000 + 100)  # 简单算法生成不同的起始价格
        except ValueError:
            # 如果股票代码不是纯数字（如美股），使用默认价格
            base_price = 200

        price = base_price

        for i in range(30):
            date = current_date - datetime.timedelta(days=i)

            # 生成当天价格浮动
            daily_change_percent = random.uniform(-2.0, 2.0)  # 每天涨跌幅范围
            daily_change = price * daily_change_percent / 100.0

            # 计算各项价格
            open_price = price
            close_price = price + daily_change
            high_price = max(open_price, close_price) * random.uniform(1.01, 1.03)  # 最高价比开盘/收盘价高1-3%
            low_price = min(open_price, close_price) * random.uniform(0.97, 0.99)  # 最低价比开盘/收盘价低1-3%

            # 添加到数据列表
            mock_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": random.randint(1000000, 5000000)
            })

            # 更新价格为当天收盘价，作为下一天的基准
            price = close_price

        # 按日期顺序返回（从早到晚）
        mock_data.reverse()
        return jsonify(mock_data)
    except Exception as e:
        print(f"获取股票数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 现有的API端点
@app.route('/api/news/<company>', methods=['GET'])
def get_company_news(company):
    try:
        company_input = unquote(company)
        
        # 處理公司識別 - 既可以處理代號也可以處理名稱
        company_name = None
        
        # 1. 檢查是否為股票代號 (如 2330)
        if company_input in stock_symbols_to_name:
            company_name = stock_symbols_to_name[company_input]
        else:
            # 2. 檢查是否為股票名稱 (如 台積電)
            # 建立反向映射 (名稱->代號)
            name_to_code = {v: k for k, v in stock_symbols_to_name.items()}
            if company_input in name_to_code:
                company_name = company_input
            else:
                # 3. 嘗試組合搜尋 (如 2330台積電)
                for code, name in stock_symbols_to_name.items():
                    combined = f"{code}{name}"
                    if company_input == combined:
                        company_name = name
                        break
        
        # 如果還沒找到公司名稱，就使用輸入值
        if not company_name:
            company_name = company_input
            
        print(f"搜尋公司: 輸入={company_input}, 識別為={company_name}")
        
        # 載入新聞資料
        try:
            with open('combined_news.json', 'r', encoding='utf-8') as f:
                all_news = json.load(f)
                print(f"成功載入 {len(all_news)} 筆新聞")
        except FileNotFoundError:
            print("找不到 combined_news.json，使用 news_service 載入")
            all_news = news_service.load_news_data()
        
        # 過濾公司新聞 - 使用多種策略匹配
        company_news = []
        
        for news in all_news:
            news_company = news.get('company', '')
            should_include = False
            
            # 匹配策略
            if news_company:
                # 1. 完全匹配
                if news_company == company_name:
                    should_include = True
                # 2. 如果新聞公司名含有股票代碼+名稱形式 (如 "2330台積電")
                elif company_input in news_company or company_name in news_company:
                    should_include = True
                # 3. 代號匹配 (假設新聞只有代號)
                elif company_input in stock_symbols_to_name and news_company == company_input:
                    should_include = True
            
            if should_include:
                # 確保所有必要欄位存在
                if 'date' not in news:
                    news['date'] = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
                
                if 'title' not in news:
                    if 'text' in news:
                        news['title'] = news['text'][:20] + '...'
                    else:
                        news['title'] = f"關於{company_name}的新聞"
                
                if 'content' not in news and 'text' in news:
                    news['content'] = news['text']
                
                if 'text' not in news and 'content' in news:
                    news['text'] = news['content']
                
                if 'impact_pct' not in news:
                    news['impact_pct'] = random.randint(40, 70)
                
                # 設定或更新公司名稱為標準化名稱
                news['company'] = company_name
                company_news.append(news)
        
        # 如果找不到相關新聞，生成模擬數據
        if not company_news:
            print(f"沒有找到 {company_name} 的相關新聞，生成模擬數據")
            for i in range(5):
                mock_news = {
                    "company": company_name,
                    "date": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
                    "title": f"{company_name}相關新聞 #{i+1}",
                    "content": f"這是關於{company_name}的模擬新聞內容，用於測試顯示。",
                    "text": f"這是關於{company_name}的模擬新聞內容 #{i+1}，這只是測試數據。",
                    "impact_pct": random.randint(40, 70)
                }
                company_news.append(mock_news)
        
        # 根據日期排序，最新的在前
        company_news.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return jsonify(company_news)
        
    except Exception as e:
        print(f"獲取新聞時出錯: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 新增API端点: 获取股票代码到名称的映射
@app.route('/api/company-mappings', methods=['GET'])
def get_company_mappings():
    try:
        return jsonify(stock_symbols_to_name)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 新增API端点: 获取台湾股票分类
@app.route('/api/tw-stock-categories', methods=['GET'])
def get_tw_stock_categories():
    try:
        data = load_tw_stock_categories()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 新增API端点: 获取台湾上市股票
@app.route('/api/tw-stocks', methods=['GET'])
def get_tw_stocks():
    try:
        stocks = load_twse_listed_stocks()
        return jsonify(stocks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 新增API端点: 获取美国股票分类
@app.route('/api/us-stock-categories', methods=['GET'])
def get_us_stock_categories():
    try:
        data = load_us_stock_categories()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 新增API端点: 获取美国股票列表
@app.route('/api/us-stocks', methods=['GET'])
def get_us_stocks():
    try:
        stocks = load_us_stock_list()
        return jsonify(stocks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 新增API端点: 搜索股票
@app.route('/api/search-stocks', methods=['GET'])
def search_stocks():
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify([]), 400

        # 整合台湾和美国股票数据进行搜索
        tw_stocks = load_twse_listed_stocks()
        us_stocks = load_us_stock_list()

        results = []

        # 搜索台湾股票
        for stock in tw_stocks:
            ticker = str(stock['有價證券代號'])
            name = stock['有價證券名稱']

            if query in ticker.lower() or query in name.lower():
                results.append({
                    "symbol": ticker,
                    "name": name,
                    "market": "TW",
                    "industry": stock.get('產業別', '')
                })

        # 搜索美国股票
        for stock in us_stocks:
            ticker = stock['Symbol']
            en_name = stock['English name']
            cn_name = stock['Chinese name']

            if query in ticker.lower() or (en_name and query in en_name.lower()) or (
                    cn_name and query in cn_name.lower()):
                results.append({
                    "symbol": ticker,
                    "name": en_name,
                    "chinese_name": cn_name,
                    "market": "US",
                    "industry": stock.get('Industry', '')
                })

        # 只返回前20个结果
        return jsonify(results[:20])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analyze/sentiment', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.json
        if not data:
            return jsonify({
                "error": "未收到請求數據",
                "sentiment": "neutral",
                "summary": "無數據可供分析",
                "suggestions": ["請提供完整的分析數據"]
            }), 400

        company = data.get('company')
        news_list = data.get('news', [])

        if not company or not news_list:
            return jsonify({
                "error": "缺少必要參數",
                "sentiment": "neutral",
                "summary": "參數不完整",
                "suggestions": ["請提供公司名稱和新聞數據"]
            }), 400

        # 使用 Gemini 服務進行分析
        try:
            result = gemini_service.analyze_sentiment(company, news_list)
            return jsonify(result)
        except Exception as e:
            print(f"Gemini 分析過程發生錯誤: {str(e)}")
            return jsonify({
                "error": str(e),
                "sentiment": "neutral",
                "summary": "AI 分析過程發生錯誤",
                "suggestions": ["請稍後重試"]
            }), 500

    except Exception as e:
        print(f"請求處理過程發生錯誤: {str(e)}")
        return jsonify({
            "error": str(e),
            "sentiment": "neutral",
            "summary": "系統錯誤",
            "suggestions": ["請稍後重試"]
        }), 500
# 修改 get_companies 函数以支持分页
@app.route('/api/companies', methods=['GET'])
def get_companies():
    try:
        # 获取市场参数，如果没有则默认为TW
        market = request.args.get('market', 'TW').upper()

        # 分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        # 计算分页索引
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        if market == 'TW':
            # 读取台湾股票数据
            stocks = load_twse_listed_stocks()
            total_count = len(stocks)

            # 分页处理
            paginated_stocks = stocks[start_index:end_index]
            companies = []

            for stock in paginated_stocks:
                ticker = str(stock['有價證券代號'])
                companies.append({
                    "symbol": ticker,
                    "name": stock['有價證券名稱'],
                    "industry": stock.get('產業別', ''),
                    # 模拟价格数据
                    "price": round(random.uniform(100, 1000), 2),
                    "change": round(random.uniform(-10, 10), 2)
                })
        elif market == 'US':
            # 读取美国股票数据
            stocks = load_us_stock_list()
            total_count = len(stocks)

            # 分页处理
            paginated_stocks = stocks[start_index:end_index]
            companies = []

            for stock in paginated_stocks:
                companies.append({
                    "symbol": stock['Symbol'],
                    "name": stock['English name'],
                    "chinese_name": stock['Chinese name'],
                    "industry": stock.get('Industry', ''),
                    # 模拟价格数据
                    "price": round(random.uniform(100, 1000), 2),
                    "change": round(random.uniform(-10, 10), 2)
                })
        else:
            return jsonify({"error": "不支持的市场参数"}), 400

        # 返回结果，包含分页信息
        return jsonify({
            "data": companies,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_count,
                "total_pages": math.ceil(total_count / page_size)
            }
        })
    except Exception as e:
        print(f"载入公司列表时发生错误: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # 在启动应用之前初始化数据
    initialize_data()

    print("启动 Flask 服务器...")
    app.run(host='0.0.0.0', port=5001, debug=True)


