from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Any, Dict

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
    print(f"Received request: {req_json}")

    rpc_request = RPCRequest(**req_json)

    if rpc_request.method == "testConnection":
        response = {"jsonrpc": "2.0", "result": "Connection successful", "id": rpc_request.id}
        print(f"Response: {response}")
        return response

    elif rpc_request.method == "testExchangeConnection":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.options(
                    EXCHANGE_ACTIVESYNC_URL,
                    auth=(USERNAME, PASSWORD),
                    headers={
                        "Content-Type": "application/vnd.ms-sync.wbxml",
                        "MS-ASProtocolVersion": "14.0"
                    }
                )
            if response.status_code == 200:
                result = {
                    "jsonrpc": "2.0",
                    "result": "Exchange ActiveSync connection successful",
                    "id": rpc_request.id
                }
            else:
                result = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": response.status_code,
                        "message": f"Exchange returned error: {response.status_code}"
                    },
                    "id": rpc_request.id
                }
            print(f"Response: {result}")
            return result

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": rpc_request.id
            }
            print(f"Error Response: {error_response}")
            return error_response

    error_response = {
        "jsonrpc": "2.0",
        "error": {"code": -32601, "message": "Method not found"},
        "id": rpc_request.id
    }
    print(f"Error Response: {error_response}")
    return error_response
