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
            # 改回使用 gemini-pro
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            
            # 設定生成參數
            self.generation_config = {
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 2048,
            }
            
        except Exception as e:
            raise Exception(f"Gemini 初始化失敗: {str(e)}")

    def analyze_sentiment(self, company, news_list):
        try:
            # 準備新聞摘要
            news_summary = "\n".join([
                f"- {news.get('date', 'N/A')}: {news.get('text', '')[:100]}... "
                f"(情感分數: {news.get('impact_pct', 0)}%)"
                for news in news_list[:5]
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

            print(f"發送提示詞到 Gemini 1.5...")

            # 使用設定的參數調用 API
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            if not response or not response.text:
                raise Exception("Gemini API 回應為空")

            print(f"收到 Gemini 回應: {response.text}")

            try:
                cleaned_text = response.text.strip('`').strip()
                if cleaned_text.startswith('json'):
                    cleaned_text = cleaned_text[4:].strip()
                
                result = json.loads(cleaned_text)
                
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