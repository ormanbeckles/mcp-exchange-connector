from fastapi import FastAPI
from fastmcp import FastMCP
import json

# Initialize FastAPI
app = FastAPI()

# Initialize FastMCP
mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

# Load your records
RECORDS = json.load(open("records.json"))
LOOKUP = {r["id"]: r for r in RECORDS}

# Define 'search' explicitly with correct schema
@mcp.tool()
async def search(query: str):
    results = []
    tokens = query.lower().split()
    for record in RECORDS:
        searchable_text = " ".join([
            record.get("title", ""),
            record.get("text", ""),
            " ".join(record.get("metadata", {}).values())
        ]).lower()
        if any(token in searchable_text for token in tokens):
            results.append({
                "id": record["id"],
                "title": record["title"],
                "text": record["text"],
                "url": None
            })
    return {"results": results}

# Define 'fetch' explicitly with correct schema
@mcp.tool()
async def fetch(id: str):
    if id not in LOOKUP:
        raise ValueError("unknown id")
    record = LOOKUP[id]
    return {
        "id": record["id"],
        "title": record["title"],
        "text": record["text"],
        "url": None,
        "metadata": record.get("metadata", {})
    }

# Attach MCP router explicitly to FastAPI app
app.include_router(mcp.router)
