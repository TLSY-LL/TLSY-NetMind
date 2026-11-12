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
            except:
                return text_data
        return None

@app.post("/v1/eveng/nodes/{lab_path:path}/start")
async def start_nodes(lab_path: str):
    if not lab_path.startswith("/"):
        lab_path = "/" + lab_path

    nodes_data = await call_mcp("list_lab_nodes", {"lab_path": lab_path})
    
    # 如果底层直接返回了字典，且包含 data
    if isinstance(nodes_data, dict) and "data" in nodes_data:
        raw_data = nodes_data["data"]
        
        # 如果 data 是字典（类似 {"1": {...}, "2": {...}}）
        if isinstance(raw_data, dict):
            nodes_list = list(raw_data.values())
        # 如果 data 是列表（类似 [{...}, {...}]）
        elif isinstance(raw_data, list):
            nodes_list = raw_data
        else:
            return {"status": "error", "message": "data 字段格式未知", "raw": raw_data}

        started = []
        for node in nodes_list:
            if isinstance(node, dict) and "id" in node:
                node_id = node["id"]
                await call_mcp("start_node", {"lab_path": lab_path, "node_id": node_id})
                started.append(node_id)
        
        if started:
            return {"status": "success", "message": f"已发送启动指令，节点 ID: {started}"}
        else:
            return {"status": "error", "message": "没有找到包含 id 的节点信息"}
            
    return {"status": "error", "message": "底层返回格式不对或报错", "raw": nodes_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)

