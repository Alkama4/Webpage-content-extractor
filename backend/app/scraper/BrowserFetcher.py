from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Browser, BrowserContext

class BrowserFetcher:
    def __init__(self, user_agent: str = "MyScraperBot"):
        self.user_agent = user_agent
        self._robots_cache = {}
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._playwright = None

    async def start(self):
        """Initialize Playwright and the browser once."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch()
        self._context = await self._browser.new_context(user_agent=self.user_agent)

    async def fetch(self, url: str) -> str:
        if not self._context:
            raise RuntimeError("BrowserFetcher not started. Call 'await start()' first.")

        if not await self._is_allowed(url):
            raise PermissionError(f"Access to {url} is blocked by robots.txt")

        page = await self._context.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await page.close()
        return html

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

    async def stop(self):
        """Close the browser and stop Playwright."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
