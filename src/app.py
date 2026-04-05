import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os

app = FastAPI(title="Support Ticket Portal")
N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://n8n:5678")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/webhook/support-ticket")
async def proxy_to_n8n(request: Request):
    """
    Proxies the incoming multipart/form-data (ticket + optional PDF) to n8n.
    """
    content_type = request.headers.get("Content-Type")
    
    # We use a stream-based approach or just forward the raw body for efficiency
    target_url = f"{N8N_BASE_URL}/webhook/support-ticket"
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward the exact headers (including boundary) and the raw body
            response = await client.post(
                target_url,
                content=await request.body(),
                headers={"Content-Type": content_type},
                timeout=60.0
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"n8n connectivity error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
