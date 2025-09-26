from .webpage import WebpageBase, WebpageCreate, WebpageInDB, WebpagePatch
from .scrape import ScrapeBase, ScrapeCreate, ScrapeInDB
from .scrape_data import ScrapeData

__all__ = [
    "WebpageBase", "WebpageCreate", "WebpageInDB", "WebpagePatch",
    "ScrapeBase", "ScrapeCreate", "ScrapeInDB",
    "ScrapeData",
]
