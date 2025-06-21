from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Any, Dict, List

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Dict[str, Any] = {}
    id: int

EXCHANGE_ACTIVESYNC_URL = "https://west.EXCH092.serverdata.net/Microsoft-Server-ActiveSync"
USERNAME = os.getenv("EAS_USERNAME")
PASSWORD = os.getenv("EAS_PASSWORD")

@app.get("/")
async def root():
    return {"status": "MCP Exchange Connector server running"}

@app.post("/")
async def handle_rpc(request: Request):
    req_json = await request.json()
    rpc_request = RPCRequest(**req_json)

    if rpc_request.method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "capabilities": {
                    "methods": ["search", "fetch"],
                    "protocolVersion": "2025-03-26"
                }
            },
            "id": rpc_request.id
        }

    elif rpc_request.method == "search":
        query = rpc_request.params.get("query", "")
        # Placeholder search implementation
        results = [{"id": "email-123", "title": "Test Email", "text": "This is a test email from Exchange.", "url": None}]
        return {
            "jsonrpc": "2.0",
            "result": {"results": results},
            "id": rpc_request.id
        }

    elif rpc_request.method == "fetch":
        resource_id = rpc_request.params.get("id", "")
        # Placeholder fetch implementation
        if resource_id == "email-123":
            resource = {
                "id": "email-123",
                "title": "Test Email",
                "text": "Full content of the test email.",
                "url": None,
                "metadata": {"sender": "example@example.com"}
            }
            return {"jsonrpc": "2.0", "result": resource, "id": rpc_request.id}
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": "Resource not found"},
                "id": rpc_request.id
            }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": rpc_request.id
    }
