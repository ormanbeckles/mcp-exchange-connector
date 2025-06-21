from fastmcp import FastMCP
from fastapi import FastAPI
import json

app = FastAPI()
mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")
RECORDS = json.load(open("records.json"))
LOOKUP = {r["id"]: r for r in RECORDS}

@mcp.tool()
async def search(query: str):
    toks = query.lower().split()
    results = []
    for r in RECORDS:
        hay = " ".join([r.get("title", ""), r.get("text", ""), " ".join(r.get("metadata", {}).values())]).lower()
        if any(t in hay for t in toks):
            results.append({
                "id": r["id"],
                "title": r["title"],
                "text": r["text"],
                "url": None
            })
    return {"results": results}

@mcp.tool()
async def fetch(id: str):
    if id not in LOOKUP:
        raise ValueError("unknown id")
    r = LOOKUP[id]
    return {
        "id": r["id"],
        "title": r["title"],
        "text": r["text"],
        "url": None,
        "metadata": r.get("metadata", {})
    }

app.include_router(mcp.router)
