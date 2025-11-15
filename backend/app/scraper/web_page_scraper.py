from bs4 import BeautifulSoup
from .BrowserFetcher import BrowserFetcher
from .ErrorClasses import PageNotLoadedError, ElementNotFoundError

class WebPageScraper:
    def __init__(self, fetcher: BrowserFetcher):
        self._html = None
        self.fetcher = fetcher

    async def load(self, url: str):
        self.url = url.rstrip('/')
        self._html = await self.fetcher.fetch(self.url)

    def scrape(self, selector: str) -> str:
        """
        Return the *text* of the first element that matches `selector`.
        Raises an ElementNotFoundError if the element doesn't exist.
        """
        if not self._html:
            raise PageNotLoadedError("Call 'await load()' before scraping.")

        soup = BeautifulSoup(self._html, "html.parser")
        elem = soup.select_one(selector)
        if elem:
            return elem.get_text(strip=True)
        else:
            raise ElementNotFoundError(selector, self.url)
