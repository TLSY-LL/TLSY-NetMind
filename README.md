# 🧠 TLSY-NetMind: 智能网络运维平台 (NetOps Copilot)

> **TLSY 品牌技术矩阵**：本项目与 [TLSY-Cloud](https://github.com/TLSY-LL/TLSY-Cloud) 共同构成 **“云网一体化 AIOps 解决方案”**。`TLSY-Cloud` 负责容器化基础设施与 DevOps 流水线，`TLSY-NetMind` 则聚焦于网络设备的智能感知与自动化闭环。

基于大语言模型（LLM）与模型上下文协议（MCP）的**网络智能运维大脑**。实现了从“真实设备异常感知 -> 监控告警 -> AI智能诊断 -> MCP自动化下发”的完整 NetOps 闭环。

## 🏗️ 核心架构
- **前端展示**：Flask + 原生 HTML/JS，集成 Grafana 监控与 Dify 原生对话窗口。
- **AI 编排引擎**：Dify + Ollama (本地部署 Qwen2.5-7B 大模型)，结合 RAG 私有排障知识库。
- **监控与日志**：Prometheus + Grafana + Loki，实时抓取宿主机指标与设备 Syslog 日志。
- **自动化执行**：MCP (Model Context Protocol) + FastAPI 代理，打通底层 EVE-NG/eNSP 网络设备。
- **网络仿真**：EVE-NG / eNSP 虚拟化环境，提供真实的锐捷/华为/思科设备日志源。

## 🚀 懒人式一键部署

### 1. 初始化网络
```bash
docker network create lac_net
2. 启动监控栈 (Loki/Prometheus/Grafana)
bash
cd monitor
docker compose up -d
3. 启动 AIOps 驾驶舱
bash
cd ../dashboard
cp .env.example .env
# 👉 编辑 .env 文件，填入你的 Dify API Key 以及宿主机 IP
docker compose up -d --build
4. 全自动脚本 (可选)
在根目录直接运行：

bash
./start.sh
💡 演示截图
(在这里放上你的明亮版驾驶舱截图)
