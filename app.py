from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "MCP server running."}

@app.post("/")
async def mcp_endpoint(request: Request):
    body = await request.json()
    method = body.get("method", "")
    if method == "search":
        return {
            "jsonrpc": "2.0",
            "result": {
                "results": [
                    {
                        "id": "1",
                        "title": "Sample Order",
                        "text": "This is a cupcake order",
                        "url": None
                    }
                ]
            },
            "id": body.get("id")
        }
    elif method == "fetch":
        return {
            "jsonrpc": "2.0",
            "result": {
                "id": "1",
                "title": "Sample Order",
                "text": "Full details of the cupcake order.",
                "url": None,
                "metadata": {}
            },
            "id": body.get("id")
        }
    else:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": body.get("id")
        }
