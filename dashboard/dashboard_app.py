from flask import Flask, render_template, request, jsonify
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Dify 配置
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_CHAT_KEY = os.getenv("DIFY_CHAT_KEY")
DIFY_URL = os.getenv("DIFY_URL")
# 聊天助手的 API 地址通常是工作流地址的 /chat-messages
DIFY_CHAT_URL = DIFY_URL.replace("/workflows/run", "/chat-messages") if DIFY_URL else ""

LOKI_URL = os.getenv("LOKI_URL")

@app.route('/')
def index():
    return render_template('index.html')

# --- 原有：获取告警流 ---
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    now = int(time.time() * 10**9)
    start = now - (60 * 60 * 10**9)
    params = {"query": '{job="real_device"}', "start": start, "end": now, "limit": 10, "direction": "backward"}
    try:
        response = requests.get(LOKI_URL, params=params, timeout=5)
        data = response.json()
        streams = data["data"]["result"]
        alerts = []
        for stream in streams:
            for value in stream["values"]:
                log_text = value[1]
                level = "CRITICAL" if "down" in log_text or "CHANGED" in log_text else "INFO"
                alerts.append({
                    "id": value[0], 
                    "time": time.strftime("%H:%M:%S", time.localtime(int(value[0])/10**9)),
                    "device": "Ruijie-RSR", 
                    "level": level, 
                    "msg": log_text
                })
        return jsonify(alerts)
    except Exception as e:
        return jsonify([])

# --- 原有：智能诊断工作流分析 ---
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    alert_msg = data.get("msg")
    dify_payload = {"inputs": {"syslog_text": alert_msg}, "response_mode": "blocking", "user": "Dashboard_User"}
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(DIFY_URL, headers=headers, json=dify_payload, timeout=600)
        if response.status_code == 200:
            return jsonify({"status": "success", "report": response.json()["data"]["outputs"]["text"]})
        return jsonify({"status": "error", "message": "Dify API Error"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- 新增：原生 AI 助手聊天接口 ---
@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message")
    if not DIFY_CHAT_KEY:
        return jsonify({"status": "error", "message": "环境变量中未配置 DIFY_CHAT_KEY"})
    
    payload = {
        "inputs": {},
        "query": user_msg,
        "response_mode": "blocking",
        "user": "dashboard_user"
    }
    headers = {"Authorization": f"Bearer {DIFY_CHAT_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(DIFY_CHAT_URL, headers=headers, json=payload, timeout=600)
        if response.status_code == 200:
            return jsonify({"status": "success", "answer": response.json().get("answer", "")})
        return jsonify({"status": "error", "message": f"Dify API Error: {response.status_code}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
