import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("找不到 GEMINI_API_KEY 環境變數")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            raise Exception(f"Gemini 初始化失敗: {str(e)}")

    def analyze_sentiment(self, company, news_list):
        try:
            # 準備新聞摘要
            news_summary = "\n".join([
                f"- {news.get('date', 'N/A')}: {news.get('text', '')[:100]}... "
                f"(情感分數: {news.get('impact_pct', 0)}%)"
                for news in news_list[:5]  # 只取前5則新聞
            ])

            prompt = f"""
            根據以下新聞分析 {company} 的市場情況：

            {news_summary}

            請嚴格依照以下 JSON 格式回覆，不要加入其他文字：
            {{
                "sentiment": "positive或neutral或negative",
                "summary": "50字內的分析摘要",
                "suggestions": ["投資建議1", "投資建議2"]
            }}
            """

            # 輸出提示詞以便除錯
            print(f"Prompt: {prompt}")

            # 調用 Gemini API
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Gemini API 回應為空")

            # 輸出原始回應以便除錯
            print(f"Raw response: {response.text}")

            try:
                # 清理回應文本，移除可能的 markdown 標記
                cleaned_text = response.text.strip('`').strip()
                if cleaned_text.startswith('json'):
                    cleaned_text = cleaned_text[4:].strip()
                
                result = json.loads(cleaned_text)
                
                # 驗證回應格式
                required_fields = ['sentiment', 'summary', 'suggestions']
                if not all(field in result for field in required_fields):
                    raise ValueError("回應缺少必要欄位")
                
                return result
                
            except json.JSONDecodeError as je:
                print(f"JSON 解析錯誤: {str(je)}")
                return {
                    "sentiment": "neutral",
                    "summary": "AI回應格式錯誤",
                    "suggestions": ["請稍後重試"]
                }

        except Exception as e:
            print(f"Gemini 分析失敗: {str(e)}")
            return {
                "sentiment": "neutral",
                "summary": f"分析失敗: {str(e)}",
                "suggestions": ["系統暫時無法提供分析，請稍後重試"]
            }