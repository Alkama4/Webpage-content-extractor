from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routers import webpages_router, elements_router, root_router
from app.lifespan import lifespan

app = FastAPI(root_path="/api", lifespan=lifespan)

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
