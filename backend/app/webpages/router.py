# webpages/routers.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_websites():

    # Some logic

    return {
        'values': [1, 2, 3]
    }