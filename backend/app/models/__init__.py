from .webpage import WebpageBase, WebpageCreate, WebpageInDB, WebpagePatch, WebpageOut
from .scrape import ScrapeBase, ScrapeCreate, ScrapeInDB, ScrapePatch, ScrapeOut
from .scrape_data import ScrapeData

__all__ = [
    "WebpageBase", "WebpageCreate", "WebpageInDB", "WebpagePatch", "WebpageOut",
    "ScrapeBase", "ScrapeCreate", "ScrapeInDB", "ScrapePatch", "ScrapeOut",
    "ScrapeData",
]
