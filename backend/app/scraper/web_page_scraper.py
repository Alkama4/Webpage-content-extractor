from bs4 import BeautifulSoup
from .BrowserFetcher import BrowserFetcher

class WebPageScraper:
    def __init__(self, fetcher: BrowserFetcher):
        self._html = None
        self.fetcher = fetcher

    async def load(self, url: str):
        self.url = url.rstrip('/')
        self._html = await self.fetcher.fetch(self.url)

    def scrape(self, selector: str):
        """
        Return the *text* of the first element that matches `selector`.
        If nothing is found, prints a message and returns None.
        """
        if not self._html:
            raise RuntimeError("Page not loaded. Call 'await load()' first.")
        soup = BeautifulSoup(self._html, "html.parser")
        elem = soup.select_one(selector)
        if elem:
            return elem.get_text(strip=True)
        else:
            print(f"Warning: No element found for selector '{selector}' on {self.url}")
            return None
