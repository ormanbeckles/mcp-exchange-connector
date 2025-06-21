from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json

app = FastAPI()

with open("records.json", "r") as file:
    RECORDS = json.load(file)

LOOKUP = {r["id"]: r for r in RECORDS}

@app.get("/")
async def root():
    return {"status": "MCP server is running"}

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
