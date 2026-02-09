from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx
import os

app = FastAPI(title="JobNexAI Control Center")
templates = Jinja2Templates(directory="templates")

# URLs / endpoints via variables d'env (Coolify)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
VIBE_URL = os.getenv("VIBE_URL", "http://vibe:3000/health")
CLAUDE_URL = os.getenv("CLAUDE_URL", "https://api.anthropic.com/v1/messages")
OPENAI_URL = os.getenv("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
N8N_URL = os.getenv("N8N_URL", "http://n8n:5678")
FIRECRAWL_URL = os.getenv("FIRECRAWL_URL", "http://firecrawl:3002/health")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def check_http(url: str, method: str = "GET", timeout: float = 2.0, payload: dict | None = None):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                r = await client.get(url)
            else:
                r = await client.post(url, json=payload or {})
        return {"ok": True, "status_code": r.status_code, "body": r.json() if "application/json" in r.headers.get("content-type", "") else r.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/status")
async def status():
    services = {}

    services["ollama"] = await check_http(f"{OLLAMA_URL}/api/tags")
    services["vibe"] = await check_http(VIBE_URL)
    services["claude"] = await check_http(CLAUDE_URL)
    services["openai"] = await check_http(OPENAI_URL)
    services["n8n"] = await check_http(N8N_URL)
    services["firecrawl"] = await check_http(FIRECRAWL_URL)

    return JSONResponse(services)


@app.post("/api/ollama/generate")
async def ollama_generate(prompt: str, model: str | None = None):
    payload = {
        "model": model or os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b"),
        "prompt": prompt
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
    return JSONResponse(r.json())
