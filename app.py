from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RPC(BaseModel):
    jsonrpc: str
    method: str
    params: Dict[str, Any] = {}
    id: int

with open("records.json") as f:
    RECORDS = json.load(f)

@app.get("/")
async def root():
    return {"status": "Cupcake MCP server running"}

@app.post("/")
async def handle_rpc(request: Request):
    req_json = await request.json()
    rpc = RPC(**req_json)

    if rpc.method == "initialize":
        return {
            "jsonrpc": "2.0",
            "result": {
                "capabilities": {
                    "methods": ["search", "fetch"],
                    "protocolVersion": "2025-03-26"
                }
            },
            "id": rpc.id
        }

    elif rpc.method == "search":
        query = rpc.params.get("query", "").lower()
        results = [
            {
                "id": rec["id"],
                "title": rec["title"],
                "text": rec["text"],
                "url": rec["url"]
            }
            for rec in RECORDS
            if query in rec["title"].lower() or query in rec["text"].lower()
        ]
        return {
            "jsonrpc": "2.0",
            "result": {"results": results},
            "id": rpc.id
        }

    elif rpc.method == "fetch":
        record_id = rpc.params.get("id", "")
        record = next((r for r in RECORDS if r["id"] == record_id), None)
        if record:
            return {
                "jsonrpc": "2.0",
                "result": record,
                "id": rpc.id
            }
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Not found"},
            "id": rpc.id
        }

    return {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": rpc.id
    }
