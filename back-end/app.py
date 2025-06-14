from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允許前端跨域請求

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def analyze_with_gemini(text):
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": text
            }]
        }]
    }
    
    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"API 請求失敗: {response.status_code}")

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    user_text = data.get("text", "")

    if not user_text:
        return jsonify({'error': '請提供 text 欄位'}), 400

    try:
        result = analyze_with_gemini(user_text)
        return jsonify({'response': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
