# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import webpages_router, scrapes_router

app = FastAPI(root_path="")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webpages_router, prefix="/webpages", tags=["webpages"])
app.include_router(scrapes_router, prefix="/scrapes", tags=["scrapes"])


@app.get("/")
def root():
    return {
        'msg': 'Hello world!'
    }
