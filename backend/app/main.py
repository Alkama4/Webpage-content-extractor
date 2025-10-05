from fastapi import FastAPI, Response
import httpx
from fastapi.middleware.cors import CORSMiddleware

# Import the routers
from app.routers import webpages_router, elements_router

app = FastAPI(root_path="")

# Allow CORS from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(webpages_router)
app.include_router(elements_router)

# Root
@app.get("/")
def root():
    """
    Basic landing endpoint. Visit the API docs at /docs or /redoc.
    """
    return {"msg": "Hello world! See /docs for interactive documentation."}

@app.get("/preview")
async def preview(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
    return Response(content=resp.text, media_type="text/html")