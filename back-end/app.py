import pandas as pd
import json
import datetime
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from urllib.parse import unquote
import math
import yfinance as yf
from datetime import datetime, timedelta

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
        
        # 處理台灣股票代號 (加上.TW)
        if symbol_name.isdigit() or (symbol_name in stock_symbols_to_name):
            # 台股加上.TW後綴
            yf_symbol = f"{symbol_name}.TW"
        else:
            # 美股不需要特殊處理
            yf_symbol = symbol_name
        
        print(f"獲取股票資料: {symbol_name} (Yahoo Finance 代號: {yf_symbol})")
        
        # 設定日期範圍 - 預設抓取過去一年的資料
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        try:
            # 從 Yahoo Finance 抓取股價資料
            stock = yf.Ticker(yf_symbol)
            df = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            
            # 如果資料為空，嘗試其他可能的符號
            if df.empty and symbol_name.isdigit():
                alternative_symbols = [
                    f"{symbol_name}.TWO",  # 台灣櫃買中心
                    f"{symbol_name}.TWO.TW",
                    f"{symbol_name}.TPE"  # 台北交易所
                ]
                
                for alt_symbol in alternative_symbols:
                    print(f"嘗試替代符號: {alt_symbol}")
                    stock = yf.Ticker(alt_symbol)
                    df = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
                    if not df.empty:
                        print(f"使用替代符號 {alt_symbol} 成功")
                        break
            
            # 如果仍然沒有資料，返回模擬資料
            if df.empty:
                print(f"無法從 Yahoo Finance 抓取 {yf_symbol} 的資料，使用模擬資料")
                return generate_mock_stock_data(symbol_name)
                
            # 轉換為需要的格式
            result = []
            for index, row in df.iterrows():
                result.append({
                    "date": index.strftime('%Y-%m-%d'),
                    "open": round(float(row['Open']), 2),
                    "high": round(float(row['High']), 2),
                    "low": round(float(row['Low']), 2),
                    "close": round(float(row['Close']), 2),
                    "volume": int(row['Volume'])
                })
                
            return jsonify(result)
            
        except Exception as e:
            print(f"從 Yahoo Finance 抓取資料失敗: {str(e)}，使用模擬資料")
            return generate_mock_stock_data(symbol_name)
            
    except Exception as e:
        print(f"獲取股票資料失敗: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 抽取模擬資料生成為單獨的函數
def generate_mock_stock_data(symbol_name):
    mock_data = []
    current_date = datetime.now()
    
    # 設定起始價格
    try:
        base_price = int(int(symbol_name) % 1000 + 100)
    except ValueError:
        base_price = 200
        
    price = base_price
    
    for i in range(90):  # 生成三個月資料
        date = current_date - timedelta(days=i)
        
        daily_change_percent = random.uniform(-2.0, 2.0)
        daily_change = price * daily_change_percent / 100.0
        
        open_price = price
        close_price = price + daily_change
        high_price = max(open_price, close_price) * random.uniform(1.01, 1.03)
        low_price = min(open_price, close_price) * random.uniform(0.97, 0.99)
        
        mock_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": random.randint(1000000, 5000000)
        })
        
        price = close_price
        
    mock_data.reverse()
    return jsonify(mock_data)

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
        market = request.args.get('market', 'TW').upper()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        if market == 'TW':
            stocks = load_twse_listed_stocks()
            total_count = len(stocks)
            paginated_stocks = stocks[start_index:end_index]
            companies = []
            
            # 批量獲取股價資料
            try:
                # 構建股票代碼列表
                symbols = [f"{str(stock['有價證券代號'])}.TW" for stock in paginated_stocks]
                
                # 從 Yahoo Finance 獲取最新價格
                current_prices = get_batch_stock_prices(symbols)
                
                for stock in paginated_stocks:
                    ticker = str(stock['有價證券代號'])
                    yf_symbol = f"{ticker}.TW"
                    
                    price_info = current_prices.get(yf_symbol, {})
                    price = price_info.get('price', round(random.uniform(100, 1000), 2))
                    change = price_info.get('change', round(random.uniform(-10, 10), 2))
                    
                    companies.append({
                        "symbol": ticker,
                        "name": stock['有價證券名稱'],
                        "industry": stock.get('產業別', ''),
                        "price": price,
                        "change": change
                    })
            except Exception as e:
                print(f"獲取批量股價失敗: {str(e)}，使用模擬資料")
                # 使用模擬資料
                for stock in paginated_stocks:
                    ticker = str(stock['有價證券代號'])
                    companies.append({
                        "symbol": ticker,
                        "name": stock['有價證券名稱'],
                        "industry": stock.get('產業別', ''),
                        "price": round(random.uniform(100, 1000), 2),
                        "change": round(random.uniform(-10, 10), 2)
                    })
        
        # US market 處理類似...
        
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
        print(f"載入公司列表時發生錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 批量獲取股票價格
def get_batch_stock_prices(symbols):
    try:
        result = {}
        
        # 由於 yfinance 的批量獲取可能不穩定，每次處理 5 個股票
        batch_size = 5
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            
            # 獲取多個股票的資料
            data = yf.download(
                tickers=batch,
                period="2d",  # 僅獲取最近兩天資料以計算漲跌
                group_by="ticker",
                auto_adjust=True
            )
            
            # 處理每個股票
            for symbol in batch:
                try:
                    if len(batch) == 1:
                        # 單一股票的數據結構不同
                        df = data
                    else:
                        # 多股票的數據結構
                        df = data[symbol]
                    
                    if not df.empty and len(df) >= 2:
                        current_price = float(df['Close'].iloc[-1])
                        prev_price = float(df['Close'].iloc[-2])
                        change = round(current_price - prev_price, 2)
                        
                        result[symbol] = {
                            "price": round(current_price, 2),
                            "change": change,
                            "changePercent": round((change / prev_price) * 100, 2) if prev_price else 0
                        }
                except Exception as e:
                    print(f"處理 {symbol} 股價時出錯: {str(e)}")
        
        return result
    except Exception as e:
        print(f"批量獲取股價失敗: {str(e)}")
        return {}

@app.route('/api/market-index/<market>', methods=['GET'])
def get_market_index(market):
    try:
        if market.upper() == 'TW':
            # 使用 yfinance 獲取台灣加權指數
            index_data = yf.Ticker('^TWII')
            hist = index_data.history(period='2d')
            
            if len(hist) >= 2:
                current = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = round(current - prev, 2)
                change_percent = round((change / prev) * 100, 2)
                
                return jsonify({
                    "name": "加權指數",
                    "price": current,
                    "change": change,
                    "changePercent": change_percent
                })
                
        elif market.upper() == 'US':
            # 使用 yfinance 獲取標普 500 指數
            index_data = yf.Ticker('^GSPC')
            hist = index_data.history(period='2d')
            
            if len(hist) >= 2:
                current = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                change = round(current - prev, 2)
                change_percent = round((change / prev) * 100, 2)
                
                return jsonify({
                    "name": "S&P 500",
                    "price": current,
                    "change": change,
                    "changePercent": change_percent
                })
        
        # 如果沒有獲取到數據，返回模擬數據
        mock_data = {
            "TW": {
                "name": "加權指數",
                "price": 18902.35,
                "change": 82.45,
                "changePercent": 0.44
            },
            "US": {
                "name": "S&P 500",
                "price": 4802.35,
                "change": 12.45,
                "changePercent": 0.26
            }
        }
        
        return jsonify(mock_data.get(market.upper(), mock_data['TW']))
        
    except Exception as e:
        print(f"獲取市場指數發生錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    # 在启动应用之前初始化数据
    initialize_data()

    print("启动 Flask 服务器...")
    app.run(host='0.0.0.0', port=5001, debug=True)


