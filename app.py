from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI()

class RPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Dict[str, Any] = {}
    id: int

@app.get("/")
async def root():
    return {"status": "MCP Exchange Connector server running"}

@app.post("/")
async def handle_rpc(request: RPCRequest):
    if request.method == "testConnection":
        return {"jsonrpc": "2.0", "result": "Connection successful", "id": request.id}
    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": request.id
    }
