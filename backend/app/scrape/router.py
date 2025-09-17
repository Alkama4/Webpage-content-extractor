# scrape/routers.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_items():
    '''
    Retrieve scraped data
    '''
    return {"items": ["foo", "bar"]}

@router.post("/")
async def read_items():
    '''
    Run the scraping script
    '''
    return { "msg": "Scrape successfull!" }