from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the routers
from app.routers import webpages_router, scrapes_router

app = FastAPI(root_path="")

# Allow CORS from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(webpages_router, prefix="/webpages")
app.include_router(scrapes_router, prefix="/scrapes")

# Root
@app.get("/")
def root():
    """
    Basic landing endpoint. Visit the API docs at /docs or /redoc.
    """
    return {"msg": "Hello world! See /docs for interactive documentation."}
