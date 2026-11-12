from flask import Flask, request, jsonify
import requests
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_URL = os.getenv("DIFY_URL")
LOKI_URL = os.getenv("LOKI_URL")

def fetch_recent_logs():
    now = int(time.time() * 10**9)
    start = now - (5 * 60 * 10**9) 
    params = {"query": '{job="real_device"}', "start": start, "end": now, "limit": 5, "direction": "backward"}
    try:
        response = requests.get(LOKI_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            streams = data["data"]["result"]
            logs = [value[1] for stream in streams for value in stream["values"]]
            return "\n".join(logs) if logs else "未找到该设备近期的日志"
    except Exception as e:
        print(f"获取 Loki 日志失败: {e}")
    return "无法从 Loki 获取日志"

def process_with_dify():
    print("\n🔍 正在从 Loki 提取真实的故障日志...")
    real_logs = fetch_recent_logs()
    print(f"📄 提取到的日志:\n{real_logs}\n")
    
    dify_payload = {"inputs": {"syslog_text": real_logs}, "response_mode": "blocking", "user": "Grafana_Alert"}
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.post(DIFY_URL, headers=headers, json=dify_payload, timeout=600)
        if response.status_code == 200:
            print("\n✅ AI 分析报告：\n" + response.json()["data"]["outputs"]["text"])
        else:
            print(f"❌ Dify 请求失败: {response.text}")
    except Exception as e:
        print(f"❌ 连接 Dify 失败或超时: {e}")

@app.route('/webhook', methods=['POST'])
def handle_alert():
    print("\n🚨 收到 Grafana 告警触发信号！")
    threading.Thread(target=process_with_dify).start()
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
