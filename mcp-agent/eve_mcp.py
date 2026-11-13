from fastapi import FastAPI
import uvicorn
import json
import os
from fastmcp import Client

app = FastAPI()
MCP_URL = os.getenv("MCP_URL", "http://localhost:8002/mcp")

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

@app.get("/v1/eveng/labs")
async def get_labs():
    result = await call_mcp("list_labs", {})
    return {"status": "success", "data": result}

@app.get("/v1/eveng/nodes/{lab_path:path}")
async def get_nodes(lab_path: str):
    if not lab_path.startswith("/"):
        lab_path = "/" + lab_path
    result = await call_mcp("list_lab_nodes", {"lab_path": lab_path})
    return {"status": "success", "data": result}

@app.post("/v1/eveng/nodes/{lab_path:path}/start")
async def start_nodes(lab_path: str):
    if not lab_path.startswith("/"):
        lab_path = "/" + lab_path

    try:
        nodes_data = await call_mcp("list_lab_nodes", {"lab_path": lab_path})

        if not isinstance(nodes_data, dict):
            return {"status": "error", "message": f"非字典数据: {type(nodes_data)} - {nodes_data}"}

        if "data" not in nodes_data:
            return {"status": "error", "message": f"未找到 data 字段: {nodes_data}"}

        raw_data = nodes_data["data"]
        nodes_list = []

        if isinstance(raw_data, dict):
            nodes_list = list(raw_data.values())
        elif isinstance(raw_data, list):
            nodes_list = raw_data

        started = []
        for node in nodes_list:
            if isinstance(node, dict) and "id" in node:
                node_id = node["id"]
                await call_mcp("start_node", {"lab_path": lab_path, "node_id": node_id})
                started.append(node_id)

        return {"status": "success", "message": f"已发送启动指令，节点 ID: {started}"}

    except Exception as e:
        return {"status": "error", "message": f"异常: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
