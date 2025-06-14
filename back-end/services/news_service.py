import json
from pathlib import Path
import os

class NewsService:
    def __init__(self):
        self.data_file = Path(__file__).parent.parent /'labeled_news_lr.json'
        # 顯示當前工作目錄和檔案路徑，用於除錯
        print(f"當前工作目錄: {os.getcwd()}")
        print(f"JSON 檔案完整路徑: {self.data_file.absolute()}")
    
    def load_news_data(self):
        try:
            if not self.data_file.exists():
                raise FileNotFoundError(f"找不到檔案：{self.data_file.absolute()}")
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    print(f"成功載入 {len(data)} 筆新聞資料")
                    return data
                except json.JSONDecodeError as e:
                    raise Exception(f"JSON 格式錯誤: {str(e)}")
                
        except FileNotFoundError as e:
            print(f"檔案不存在錯誤: {str(e)}")
            raise
        except Exception as e:
            print(f"其他錯誤: {str(e)}")
            raise Exception(f"無法讀取新聞資料: {str(e)}")

    def get_news_by_index(self, index):
        news_data = self.load_news_data()
        if index < 0 or index >= len(news_data):
            raise ValueError("新聞索引超出範圍")
        return news_data[index]