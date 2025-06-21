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
async def mcp_endpoint(req: Request):
    body = await req.json()
    print(f"Incoming request: {json.dumps(body)}")
    rpc = RPC(**body)

    if rpc.method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "result": {
                "capabilities": {
                    "methods": ["search", "fetch"],
                    "protocolVersion": "2025-03-26"
                }
            },
            "id": rpc.id
        }
        print(f"Initialize response: {response}")
        return response

    if rpc.method == "search":
        q = rpc.params.get("query", "").lower()
        results = [
            {
                "id": rec["id"],
                "title": rec["title"],
                "text": rec["text"],
                "url": None
            }
            for rec in RECORDS
            if q in rec["title"].lower() or q in rec["text"].lower()
        ]
        response = {"jsonrpc": "2.0", "result": {"results": results}, "id": rpc.id}
        print(f"Search response: {response}")
        return response

    if rpc.method == "fetch":
        rid = rpc.params.get("id", "")
        rec = next((r for r in RECORDS if r["id"] == rid), None)
        if rec:
            response = {"jsonrpc": "2.0", "result": rec, "id": rpc.id}
            print(f"Fetch response: {response}")
            return response
        response = {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Not found"},
            "id": rpc.id
        }
        print(f"Fetch error response: {response}")
        return response

    response = {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": rpc.id
    }
    print(f"Unhandled method response: {response}")
    return response
