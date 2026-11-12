import socket
import requests
import time
import json

UDP_IP = "0.0.0.0"
UDP_PORT = 514
LOKI_URL = "http://loki:3100/loki/api/v1/push"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"🎧 正在监听 UDP {UDP_PORT} 端口，等待真实设备发送 Syslog...")
print("👉 去路由器里随便 shutdown 一个接口测试！\n")

while True:
    data, addr = sock.recvfrom(4096)
    log_text = data.decode('utf-8', errors='ignore').strip()
    print(f"[收到来自 {addr[0]} 的日志]: {log_text}")

    # 将真实的日志推送到 Loki
    timestamp_ns = str(int(time.time() * 10**9))
    payload = {
        "streams": [
            {
                "stream": {"job": "real_device", "device": "Ruijie-RSR"},
                "values": [[timestamp_ns, log_text]]
            }
        ]
    }
    try:
        res = requests.post(LOKI_URL, json=payload)
        if res.status_code == 204:
            print("  └── ✅ 已成功推送至 Loki 大屏")
        else:
            print(f"  └── ❌ Loki 推送失败: {res.status_code}")
    except Exception as e:
        print(f"  └── ❌ Loki 连接异常: {e}")
