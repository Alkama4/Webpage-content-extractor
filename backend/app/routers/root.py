from fastapi import APIRouter, Response
import httpx
from app.scraper.utils import ValidationData, ValidationRequest, validate_scrapes, run_scrape

router = APIRouter(prefix="", tags=["root"])


@router.get("/")
def root():
    """
    Basic landing endpoint. Visit the API docs at /docs or /redoc.
    """
    return {"msg": "Hello world! See /docs for interactive documentation."}


@router.get("/preview")
async def preview(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
    return Response(content=resp.text, media_type="text/html")


@router.get("/validate", response_model=ValidationData)
async def validate_scrapes_endpoint(req: ValidationRequest):
    """
    Run the scraper against a single page URL using the supplied list of
    CSS/XPath locators. No data is persisted - the result is returned
    directly to the caller.
    """
    return validate_scrapes(req)


@router.post("/run_active_scrapes")
async def run_active_scrapes():
    """
    Scrape all of the active webpages.
    """
    await run_scrape()
    return {
        "msg": "Scrapes completed for active webpages.",
    }
