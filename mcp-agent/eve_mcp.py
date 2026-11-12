from fastapi import FastAPI
import uvicorn
import json
import os
from fastmcp import Client

app = FastAPI()
MCP_URL = os.getenv("MCP_URL", "http://localhost:8000/mcp")

async def call_mcp(tool_name: str, arguments: dict):
    async with Client(MCP_URL) as client:
        result = await client.call_tool(tool_name, arguments)
        if result.content:
            text_data = result.content[0].text
            try:
                return json.loads(text_data)
            except Exception as e:
                print(f"⚠️ MCP 返回了无法解析的字符串: {text_data}")
                return text_data
        return None

@app.post("/v1/eveng/nodes/{lab_path:path}/start")
async def start_nodes(lab_path: str):
    if not lab_path.startswith("/"):
        lab_path = "/" + lab_path

    try:
        nodes_data = await call_mcp("list_lab_nodes", {"lab_path": lab_path})
        print(f"🔥 DEBUG: 底层返回数据 = {nodes_data}")

        if isinstance(nodes_data, str):
            return {"status": "error", "message": f"MCP 返回纯文本: {nodes_data}"}

        nodes_list = []
        if isinstance(nodes_data, dict):
            temp = nodes_data.get("data", [])
            if isinstance(temp, list):
                nodes_list = temp
            elif isinstance(temp, dict):
                nodes_list = temp.get("nodes", [])
        elif isinstance(nodes_data, list):
            nodes_list = nodes_data

        if not nodes_list:
            return {"status": "error", "message": f"未能解析到任何节点信息，原始数据: {nodes_data}"}

        started = []
        for node in nodes_list:
            if isinstance(node, dict):
                node_id = node.get("id")
                if node_id:
                    await call_mcp("start_node", {"lab_path": lab_path, "node_id": node_id})
                    started.append(node_id)
            elif isinstance(node, int):
                await call_mcp("start_node", {"lab_path": lab_path, "node_id": node})
                started.append(node)

        return {"status": "success", "message": f"已发送启动指令，节点 ID: {started}"}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"status": "error", "message": f"执行异常: {str(e)}"}

# 🔥 核心修复：补全启动入口
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
