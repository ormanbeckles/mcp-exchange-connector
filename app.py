from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("records.json") as f:
    RECORDS = json.load(f)

LOOKUP = {r["id"]: r for r in RECORDS}

@app.post("/")
async def rpc(request: Request):
    data = await request.json()
    method = data.get("method")
    params = data.get("params")
    id = data.get("id")

    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": "search",
                        "description": "Search cupcake orders by keyword",
                        "input_schema": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "fetch",
                        "description": "Fetch a cupcake order by ID",
                        "input_schema": {
                            "type": "object",
                            "properties": {"id": {"type": "string"}},
                            "required": ["id"]
                        }
                    }
                ]
            },
            "id": id
        })

    elif method == "search":
        query = params.get("query", "").lower()
        ids = [r["id"] for r in RECORDS if query in (r["title"] + r["text"]).lower()]
        results = [{"id": r["id"], "title": r["title"], "text": r["text"], "url": None} for r in RECORDS if r["id"] in ids]
        return JSONResponse({"jsonrpc": "2.0", "result": {"results": results}, "id": id})

    elif method == "fetch":
        id_param = params.get("id")
        record = LOOKUP.get(id_param)
        if not record:
            return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32000, "message": "Not Found"}, "id": id})
        return JSONResponse({"jsonrpc": "2.0", "result": record, "id": id})

    return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": id})
