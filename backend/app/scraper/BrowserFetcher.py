from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio

class BrowserFetcher:
    def __init__(self):
        self._robots_cache = {}
        self._driver = None

    async def start(self):
        """Initialize Selenium Chrome once."""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-gpu")
        self._driver = webdriver.Chrome(options=options)

    async def fetch(self, url: str) -> str:
        if not self._driver:
            raise RuntimeError("BrowserFetcher not started. Call 'await start()' first.")

        if not await self._is_allowed(url):
            raise PermissionError(f"Access to {url} is blocked by robots.txt")

        # Run blocking Selenium call in a thread to not block the async loop
        loop = asyncio.get_event_loop()
        html = await loop.run_in_executor(None, lambda: self._driver.get(url) or self._driver.page_source)
        return html

    async def stop(self):
        if self._driver:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._driver.quit)
            self._driver = None

    async def _is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path or "/"

        if base not in self._robots_cache:
            parser = RobotFileParser()
            parser.set_url(f"{base}/robots.txt")
            try:
                parser.read()
            except Exception:
                parser = None
            self._robots_cache[base] = parser

        parser = self._robots_cache[base]
        if not parser:
            return True
        return parser.can_fetch("*", path)
        