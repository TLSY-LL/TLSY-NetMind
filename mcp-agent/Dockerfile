FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
# 容器启动后执行 main.py 代理服务（它内部会去连接 mcp-server）
CMD ["python3", "main.py"]
