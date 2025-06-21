from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    params: dict
    id: int

with open("records.json") as f:
    RECORDS = json.load(f)

@app.get("/")
async def root():
    return {"status": "Cupcake MCP running"}

@app.post("/")
async def rpc_handler(request: Request):
    body = await request.json()
    rpc = RPC(**body)

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

    elif rpc.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "search",
                        "description": "Searches cupcake orders based on a keyword query.",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query."
                                }
                            },
                            "required": ["query"]
                        },
                        "output_schema": {
                            "type": "object",
                            "properties": {
                                "results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "text": {"type": "string"},
                                            "url": {"type": ["string", "null"]}
                                        },
                                        "required": ["id", "title", "text"]
                                    }
                                }
                            },
                            "required": ["results"]
                        }
                    },
                    {
                        "name": "fetch",
                        "description": "Fetches cupcake order details by ID.",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string",
                                    "description": "ID of the cupcake order."
                                }
                            },
                            "required": ["id"]
                        },
                        "output_schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "text": {"type": "string"},
                                "url": {"type": ["string", "null"]},
                                "metadata": {
                                    "type": ["object", "null"],
                                    "additionalProperties": {"type": "string"}
                                }
                            },
                            "required": ["id", "title", "text"]
                        }
                    }
                ]
            },
            "id": rpc.id
        }

    elif rpc.method == "search":
        query = rpc.params["query"].lower()
        results = []
        for rec in RECORDS:
            if query in rec["title"].lower() or query in rec["text"].lower():
                results.append({
                    "id": rec["id"],
                    "title": rec["title"],
                    "text": rec["text"],
                    "url": None
                })
        return {
            "jsonrpc": "2.0",
            "result": {"results": results},
            "id": rpc.id
        }

    elif rpc.method == "fetch":
        rec_id = rpc.params["id"]
        rec = next((r for r in RECORDS if r["id"] == rec_id), None)
        if rec:
            return {
                "jsonrpc": "2.0",
                "result": {
                    "id": rec["id"],
                    "title": rec["title"],
                    "text": rec["text"],
                    "url": None,
                    "metadata": rec.get("metadata", {})
                },
                "id": rpc.id
            }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": "Not found"
                },
                "id": rpc.id
            }

    else:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": "Method not found"
            },
            "id": rpc.id
        }
