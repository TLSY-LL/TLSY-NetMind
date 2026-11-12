#!/bin/bash
echo "🚀 正在初始化 TLSY AIOps 平台..."

if ! docker network inspect lac_net >/dev/null 2>&1; then
    echo "🌐 创建 Docker 虚拟网络 lac_net..."
    docker network create lac_net
fi

if [ ! -f "dashboard/.env" ]; then
    echo "⚠️ 未找到 dashboard/.env，已从 .env.example 自动复制。"
    cp dashboard/.env.example dashboard/.env
    echo "👉 请先修改 dashboard/.env 中的 IP 和 API Key，然后重新运行此脚本。"
    exit 1
fi

echo "📊 启动监控栈..."
cd monitor && docker compose up -d && cd ..

echo "💻 启动 AIOps 驾驶舱..."
cd dashboard && docker compose up -d --build && cd ..

echo "✅ 所有服务已启动！请访问: http://localhost:8000"
