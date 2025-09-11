from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data import router as data_router
from websites import router as websites_router

app = FastAPI(root_path="/")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router, prefix="/data", tags=["account"])
app.include_router(websites_router, prefix="/websites", tags=["account"])


@app.get("/")
def root():
    return {
        'msg': 'Hello world!'
    }