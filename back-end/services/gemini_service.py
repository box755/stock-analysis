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
        if not self.is_available():
            return self._get_fallback_analysis()
        
        try:
            # 改進：使用動態的新聞處理量
            max_news = min(10, len(news_list))
            prompt = self._create_prompt(company, news_list[:max_news])
            
            # 調整生成參數以獲得更全面的分析
            generation_config = {
                "temperature": 0.3,  # 稍微提高創造力
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 500,  # 增加輸出上限
            }
            
            # 使用安全設置調用 API
            response = self.model.generate_content(
                prompt, 
                generation_config=generation_config
            )
            
            # 處理回應
            return self._process_response(response.text)
            
        except Exception as e:
            print(f"Gemini 分析發生錯誤: {str(e)}")
            return self._get_fallback_analysis()

    def _process_response(self, response_text):
        """處理 API 回應，並確保輸出格式正確"""
        try:
            # 檢查回應是否為空
            if not response_text or response_text.isspace():
                print("收到空回應")
                return self._get_fallback_analysis()
                
            # 嘗試提取 JSON
            import re
            json_match = re.search(r'({[\s\S]*})', response_text)
            
            if json_match:
                json_text = json_match.group(1)
            else:
                # 清理回應文本中的潛在 markdown 標記
                cleaned_text = response_text.strip('`')
                if cleaned_text.startswith('json'):
                    cleaned_text = cleaned_text[4:].strip()
                else:
                    cleaned_text = response_text.strip()
                json_text = cleaned_text
            
            # 解析 JSON
            result = json.loads(json_text)
            
            # 驗證並格式化輸出
            return {
                "sentiment": result.get('sentiment', 'neutral').lower(),
                "summary": result.get('summary', '無法取得分析摘要')[:100],
                "suggestions": [(s[:80] if isinstance(s, str) else str(s)[:80]) 
                               for s in result.get('suggestions', ['資料不足'])[:2]]
            }
            
        except json.JSONDecodeError as je:
            print(f"JSON 解析錯誤: {str(je)} - 原始回應: {response_text[:100]}...")
            return self._get_fallback_analysis()
        except Exception as e:
            print(f"處理回應時發生錯誤: {str(e)}")
            return self._get_fallback_analysis()

    def _get_fallback_analysis(self):
        """獲取備用的分析結果"""
        return {
            "sentiment": "neutral",
            "summary": "系統暫時無法提供分析，請稍後重試",
            "suggestions": []
        }

    def is_available(self):
        """檢查服務是否可用"""
        # 實現服務可用性檢查的邏輯
        return True
    
    def _create_prompt(self, company, news_list):
        """建立優化的分析提示，處理更多新聞"""
        # 限制處理的新聞數量，但仍然比原來的多
        max_news = min(10, len(news_list))  # 最多處理10則新聞
        
        # 更有效率地處理新聞文本
        news_texts = []
        for i, news in enumerate(news_list[:max_news]):
            date = news.get('date', 'N/A')
            title = news.get('title', '無標題')
            # 只擷取內容的前100個字符
            content = (news.get('content') or news.get('text', ''))[:100]
            impact = news.get('impact_pct', 0)
            
            news_texts.append(f"- [{i+1}] {date}: {title} (影響: {impact}%)\n  摘要: {content}...")
        
        news_summary = "\n".join(news_texts)
        
        prompt = f"""你是一位資深的金融分析師，專精於半導體產業，請根據以下關於 {company} 的新聞摘要與影響分數，評估其近期市場情勢：

{news_summary}

請基於新聞內容分析整體情緒，並提供投資見解，以下列JSON格式回應：
{{
    "sentiment": "[positive/neutral/negative]",
    "summary": "[50字內的核心趨勢分析]",
    "suggestions": ["[具體投資建議1]", "[具體投資建議2]"]
}}

僅回傳JSON格式，不要其他文字。建議應具體且可行，如關注特定政策、財報指標或投資操作建議。
"""
        return prompt