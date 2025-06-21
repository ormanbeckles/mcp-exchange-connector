from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "MCP Exchange Connector server running"}

