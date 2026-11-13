# 🧠 TLSY-NetMind: 云网一体化智能运维平台 (NetOps Copilot)

> **TLSY 品牌技术矩阵**：本项目与 [TLSY-Cloud](https://github.com/TLSY-LL/TLSY-Cloud) 共同构成 **“云网一体化 AIOps 解决方案”**。`TLSY-Cloud` 聚焦于容器化基础设施与 K8s DevOps，`TLSY-NetMind` 则专注于网络设备的智能感知与自动化闭环。

基于大语言模型（LLM）与模型上下文协议（MCP）的**网络智能运维大脑**。实现了从“真实设备异常感知 -> 监控告警 -> AI 智能诊断 -> MCP 自动化下发”的完整 NetOps 闭环。

## 🏗️ 核心架构
- **前端展示**：Flask + 原生 HTML/JS/Bootstrap，纯手写明亮 SaaS 风格驾驶舱。
- **AI 编排引擎**：Dify + Ollama (本地部署 Qwen2.5-7B)，结合 RAG 私有排障知识库。
- **监控与日志**：Prometheus + Grafana + Loki，实时抓取宿主机指标与设备 Syslog。
- **自动化执行**：自研 FastAPI 代理 + MCP (Model Context Protocol)，打通底层网络设备。
- **网络仿真**：EVE-NG / eNSP 虚拟化环境，提供真实的锐捷/华为/思科设备日志源。

## 📂 目录结构
```text
TLSY-NetMind/
├── dashboard/          # 自研 AIOps 驾驶舱 (Web + Webhook + Syslog接收器)
├── monitor/            # Prometheus + Loki + Grafana 监控栈配置
├── mcp-agent/          # MCP Server 与自研 FastAPI 代理层 (控制 EVE-NG)
├── infrastructure/     # Dify 与 Ollama 的 Docker Compose 模板
├── start.sh            # 一键启动脚本 (自动建网、拉起全部容器)
└── README.md
🚀 懒人式一键部署指南
1. 环境依赖
Docker & Docker Compose

请确保宿主机已安装 Python3（用于部分初始化操作）

2. 准备环境变量
复制环境变量模板并填入你的真实信息（Dify API Key、宿主机 IP 等）：

bash
cd dashboard
cp .env.example .env
# 编辑 .env 文件，填入真实的 DIFY_API_KEY 和 DIFY_CHAT_KEY
3. 一键启动全部服务
在项目根目录执行 start.sh，它将自动创建 Docker 网络，并依次拉起监控栈、AI 驾驶舱和 MCP 控制通道。

bash
chmod +x start.sh
./start.sh
4. 启动底层大模型基础设施
本项目中的 infrastructure/ 提供了 Dify 与 Ollama 的模板：

Ollama: docker compose -f infrastructure/ollama-compose.yml up -d

Dify: 请参考官方文档，使用 infrastructure/dify-compose.yml 进行部署。

5. 访问驾驶舱
打开浏览器访问：http://YOUR_IP:8000

💡 核心亮点展示
感知层：EVE-NG 真实路由器产生 Syslog，Python 监听器毫秒级抓取并推送至 Loki。

诊断层：点击前端告警，Dify 自动读取上下文，结合 Ollama 本地大模型生成专家级排障报告。

执行层 (MCP)：大模型在生成报告后，通过自研 MCP 代理直接向 EVE-NG 下发 start 指令，实现网络自愈。

📸 演示截图
(在这里放上你的两张高清截图：1. 全局概览（带资产矩阵） 2. Dify工作流运行成功图)
