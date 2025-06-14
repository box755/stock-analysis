from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
from urllib.parse import unquote
from services.gemini_service import GeminiService

app = Flask(__name__)
CORS(app)

# 載入環境變數
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("警告：未設定 GEMINI_API_KEY")
    api_key = "AIzaSyCJWcJcF3cJKWW2onaVFph5Fz5UfYfV4Oc"  # 替換為您的 API key

# 配置 Gemini
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Gemini 設定錯誤: {str(e)}")

# 初始化服務
gemini_service = GeminiService()

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

@app.route('/api/stocks/<company>', methods=['GET'])
def get_stock_data(company):
    try:
        # 解碼 URL 中的中文字符
        company_name = unquote(company)
        
        # 模擬股價數據
        mock_data = []
        current_date = datetime.now()
        
        for i in range(30):
            date = current_date - timedelta(days=i)
            mock_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": random.uniform(500, 550),
                "high": random.uniform(550, 600),
                "low": random.uniform(450, 500),
                "close": random.uniform(500, 550),
                "volume": random.randint(1000000, 5000000)
            })
            
        return jsonify(mock_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/news/<company>', methods=['GET'])
def get_company_news(company):
    try:
        company_name = unquote(company)
        
        # 從 JSON 檔案讀取新聞
        with open('labeled_news_lr.json', 'r', encoding='utf-8') as f:
            all_news = json.load(f)
            
        # 過濾該公司的新聞
        company_news = [news for news in all_news if news.get('company') == company_name]
        
        if not company_news:
            return jsonify([]), 404
            
        return jsonify(company_news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/companies', methods=['GET'])
def get_companies():
    try:
        # 讀取新聞資料
        with open('labeled_news_lr.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # 整理公司資訊
        companies = []
        seen = set()
        
        for news in news_data:
            company = news.get('company')
            if company and company not in seen:
                companies.append({
                    "symbol": company,
                    "name": company,
                    # 加入隨機漲跌數據作為展示
                    "price": round(random.uniform(100, 1000), 2),
                    "change": round(random.uniform(-10, 10), 2)
                })
                seen.add(company)
        
        return jsonify(companies)
    except Exception as e:
        print(f"載入公司列表時發生錯誤: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("啟動 Flask 服務器...")
    app.run(host='0.0.0.0', port=5001, debug=True)

