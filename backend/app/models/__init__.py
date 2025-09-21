from .webpage import WebpageBase, WebpageCreate, WebpageInDB
from .scrape import ScrapeBase, ScrapeCreate, ScrapeInDB
from .scrape_data import ScrapeData

__all__ = [
    "WebpageBase", "WebpageCreate", "WebpageInDB",
    "ScrapeBase", "ScrapeCreate", "ScrapeInDB",
    "ScrapeData",
]
