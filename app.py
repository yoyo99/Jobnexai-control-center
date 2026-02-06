from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx
import os

app = FastAPI(title="JobNexAI Control Center")

templates = Jinja2Templates(directory="templates")

# Config via variables d'env (Coolify)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
VIBE_CMD = os.getenv("VIBE_CMD", "vibe")
CLAUDE_CMD = os.getenv("CLAUDE_CMD", "claude")
OPENAI_CMD = os.getenv("OPENAI_CMD", "openai")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def status():
    services = {}

    # Ollama
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
        services["ollama"] = {"ok": True, "details": r.json()}
    except Exception as e:
        services["ollama"] = {"ok": False, "error": str(e)}

    # On pourrait ajouter des checks pour Vibe, Claude, n8n, etc.
    return JSONResponse(services)

@app.post("/api/ollama/generate")
async def ollama_generate(prompt: str):
    payload = {
        "model": "llama3",
        "prompt": prompt
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
    return JSONResponse(r.json())
