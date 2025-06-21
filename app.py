from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

# Load data from records.json
with open("records.json", "r") as file:
    RECORDS = json.load(file)
LOOKUP = {record["id"]: record for record in RECORDS}

class SearchQuery(BaseModel):
    query: str

class FetchRequest(BaseModel):
    id: str

@app.get("/")
async def home():
    return {"status": "running"}

@app.post("/tools/list")
async def list_tools():
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
                                    "id": {"type": "string", "description": "ID of the resource."},
                                    "title": {"type": "string", "description": "Title or headline of the resource."},
                                    "text": {"type": "string", "description": "Text snippet or summary from the resource."},
                                    "url": {"type": ["string", "null"], "description": "URL of the resource."}
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
                        "id": {"type": "string", "description": "ID of the resource."},
                        "title": {"type": "string", "description": "Title of the resource."},
                        "text": {"type": "string", "description": "Complete textual content of the resource."},
                        "url": {"type": ["string", "null"], "description": "URL of the resource."},
                        "metadata": {
                            "type": ["object", "null"],
                            "additionalProperties": {"type": "string"},
                            "description": "Optional metadata providing additional context."
                        }
                    },
                    "required": ["id", "title", "text"]
                }
            }
        ]
    }

@app.post("/search")
async def search(query: SearchQuery):
    toks = query.query.lower().split()
    results = []
    for r in RECORDS:
        hay = " ".join(
            [
                r.get("title", ""),
                r.get("text", ""),
                " ".join(r.get("metadata", {}).values()),
            ]
        ).lower()
        if any(t in hay for t in toks):
            results.append({
                "id": r["id"],
                "title": r["title"],
                "text": r["text"],
                "url": r.get("url", None)
            })
    return {"results": results}

@app.post("/fetch")
async def fetch(fetch_request: FetchRequest):
    id = fetch_request.id
    if id not in LOOKUP:
        return {"error": "unknown id"}
    r = LOOKUP[id]
    return {
        "id": r["id"],
        "title": r["title"],
        "text": r["text"],
        "url": r.get("url", None),
        "metadata": r.get("metadata", None)
    }
