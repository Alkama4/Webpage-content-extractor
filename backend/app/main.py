from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routers import webpages_router, elements_router, root_router
from app.lifespan import lifespan

app = FastAPI(root_path="", lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(webpages_router)
app.include_router(elements_router)

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
