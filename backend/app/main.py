import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
from app.routers import webpages_router, elements_router, root_router
from app.lifespan import lifespan

app = FastAPI(root_path="/api", lifespan=lifespan)

READ_ONLY_MODE = os.getenv("READ_ONLY_MODE", "").lower() == "true"

if READ_ONLY_MODE:
    @app.middleware("http")
    async def read_only_middleware(request: Request, call_next):
        if READ_ONLY_MODE and request.method not in ("GET", "OPTIONS"):
            return JSONResponse(
                status_code=405,
                content={"detail": "Read-only mode enabled"}
            )
        return await call_next(request)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(root_router)
app.include_router(webpages_router)
app.include_router(elements_router)
