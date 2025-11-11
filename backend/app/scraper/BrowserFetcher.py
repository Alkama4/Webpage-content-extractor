from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
import asyncio
import httpx

class BrowserFetcher:
    def __init__(self, method: str = "httpx"):
        """
        method: "selenium" for a real browser, "httpx" for plain HTTP requests.
        """
        self._robots_cache = {}
        self._driver = None
        self._method = method.lower()
        if self._method not in ("selenium", "httpx"):
            raise ValueError("method must be 'selenium' or 'httpx'")

    async def start(self):
        """Initialize Selenium Chrome if using Selenium."""
        # if self._method == "selenium" and not self._driver:
        #     options = Options()
        #     options.add_argument("--headless=new")
        #     options.add_argument("--no-sandbox")
        #     options.add_argument("--disable-setuid-sandbox")
        #     options.add_argument("--disable-dev-shm-usage")
        #     options.add_argument(
        #         "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        #     )
        #     options.add_argument("--disable-gpu")
        #     self._driver = webdriver.Chrome(options=options)

    async def fetch(self, url: str, wait_selector: str = None, wait_time: int = 3) -> str:
        """
        Fetch the page and return HTML.
        If using Selenium, optionally wait for a selector before snapshot.
        """
        if not await self._is_allowed(url):
            raise PermissionError(f"Access to {url} is blocked by robots.txt")
        
        if self._method == "httpx":
            async with httpx.AsyncClient(follow_redirects=True, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
            }) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.text

        # elif self._method == "selenium":
        #     if not self._driver:
        #         raise RuntimeError("BrowserFetcher not started. Call 'await start()' first.")
        #     loop = asyncio.get_event_loop()

        #     def load_and_get_html():
        #         self._driver.get(url)
        #         if wait_selector:
        #             try:
        #                 WebDriverWait(self._driver, wait_time).until(
        #                     EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        #                 )
        #             except:
        #                 pass
        #         return self._driver.execute_script("return document.documentElement.outerHTML;")

        #     html = await loop.run_in_executor(None, load_and_get_html)
        #     return html

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
