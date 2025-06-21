from fastapi import FastAPI
from fastmcp import FastMCP
import json

with open("records.json") as f:
    RECORDS = json.load(f)
    LOOKUP = {r["id"]: r for r in RECORDS}

def create_server():
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

    @mcp.tool()
    async def search(query: str):
        toks = query.lower().split()
        ids = []
        for r in RECORDS:
            hay = " ".join(
                [
                    r.get("title", ""),
                    r.get("text", ""),
                    " ".join(r.get("metadata", {}).values()),
                ]
            ).lower()
            if any(t in hay for t in toks):
                ids.append(r["id"])
        return {"ids": ids}

    @mcp.tool()
    async def fetch(id: str):
        if id not in LOOKUP:
            raise ValueError("unknown id")
        return LOOKUP[id]

    return mcp.app
