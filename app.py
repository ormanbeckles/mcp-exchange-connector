from fastmcp import FastMCP
import json

def create_server():
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

    RECORDS = json.load(open("records.json"))
    LOOKUP = {r["id"]: r for r in RECORDS}

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

    return mcp.create_app()
