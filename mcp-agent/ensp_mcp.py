from fastapi import FastAPI
import uvicorn
import json
from fastmcp import Client

app = FastAPI()
MCP_URL = "http://<WINDOWS_IP>:8000/mcp" # TODO: 改成你 Windows 上 eNSP MCP 的地址

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

@app.get("/v1/ensp/labs")
async def get_labs():
    result = await call_mcp("list_labs", {})
    return {"status": "success", "data": result}

@app.get("/v1/ensp/nodes/{lab_path:path}")
async def get_nodes(lab_path: str):
    if not lab_path.startswith("/"):
        lab_path = "/" + lab_path
    result = await call_mcp("list_lab_nodes", {"lab_path": lab_path})
    return {"status": "success", "data": result}

@app.post("/v1/ensp/nodes/{lab_path:path}/start")
async def start_nodes(lab_path: str):
    if not lab_path.startswith("/"):
        lab_path = "/" + lab_path
    
    nodes_data = await call_mcp("list_lab_nodes", {"lab_path": lab_path})
    try:
        # 修复点：直接获取 data 列表，如果没有则返回空列表
        nodes_list = nodes_data.get("data", []) if isinstance(nodes_data, dict) else []
        
        if not nodes_list:
            return {"status": "error", "message": "实验中没有找到任何节点，请先在 EVE-NG 中添加设备"}
        
        started = []
        for node in nodes_list:
            node_id = node.get("id")
            if node_id:
                await call_mcp("start_node", {"lab_path": lab_path, "node_id": node_id})
                started.append(node_id)
        return {"status": "success", "message": f"已发送启动指令，节点 ID: {started}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
