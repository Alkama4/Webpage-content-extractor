from fastapi import APIRouter, Response
from app.scraper.utils import run_scrape
from app.scraper.BrowserFetcher import BrowserFetcher

router = APIRouter(prefix="", tags=["root"])

@router.get("/")
def root():
    """
    Basic landing endpoint. Visit the API docs at /docs or /redoc.
    """
    return {"msg": "Hello world! See /docs for interactive documentation."}


@router.get("/preview")
async def preview(url: str):
    fetcher = BrowserFetcher()
    await fetcher.start()
    
    try:
        html = await fetcher.fetch(url)
    except PermissionError:
        return Response(content="Blocked by robots.txt", status_code=403)
    finally:
        await fetcher.stop()

    return Response(content=html, media_type="text/html")


@router.post("/run_active_scrapes")
async def run_active_scrapes():
    """
    Scrape all of the active webpages.
    """
    await run_scrape()
    return {
        "msg": "Scrapes completed for active webpages.",
    }
