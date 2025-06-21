from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json

app = FastAPI()

with open("records.json", "r") as file:
    RECORDS = json.load(file)

LOOKUP = {r["id"]: r for r in RECORDS}

@app.get("/")
async def tools_list():
    return {
        "tools": [
            {
                "name": "search",
                "description": "Searches for resources using the provided query string and returns matching results.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query."}
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
                "description": "Retrieves detailed content for a specific resource identified by the given ID.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "ID of the resource to fetch."}
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
    }

@app.post("/")
async def mcp_endpoint(request: Request):
    data = await request.json()

    method = data.get("method")
    params = data.get("params", {})
    query = params.get("query", "")
    id = params.get("id", "")

    if method == "search":
        toks = query.lower().split()
        results = []
        for r in RECORDS:
            hay = " ".join([
                r.get("title", ""),
                r.get("text", ""),
                " ".join(r.get("metadata", {}).values())
            ]).lower()
            if any(t in hay for t in toks):
                results.append({"id": r["id"], "title": r["title"], "text": r["text"], "url": None})
        return JSONResponse({"results": results})

    elif method == "fetch":
        if id in LOOKUP:
            r = LOOKUP[id]
            return JSONResponse({
                "id": r["id"],
                "title": r["title"],
                "text": r["text"],
                "url": None,
                "metadata": r.get("metadata", {})
            })
        else:
            return JSONResponse({"error": "unknown id"}, status_code=400)

    else:
        return JSONResponse({"error": "Method not found"}, status_code=400)
