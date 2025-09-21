import urllib.robotparser as rp
import requests
from bs4 import BeautifulSoup

class WebPageScraper:
    def __init__(self, url: str):
        self.url = url.rstrip('/')
        self._html = None
        self._robots_parser = None

        # fetch page + robots.txt once
        self._load_page_and_robots()

        # guard against disallowed paths
        if not self._is_allowed_by_robots():
            raise PermissionError(f'Access to {self.url} is blocked by robots.txt')

    def _load_page_and_robots(self):
        # fetch page
        resp = requests.get(self.url)
        resp.raise_for_status()
        self._html = resp.text

        # fetch & parse robots.txt
        base = '/'.join(self.url.split('/')[:3]) + '/'
        rtxt_url = base + 'robots.txt'
        parser = rp.RobotFileParser()
        parser.set_url(rtxt_url)
        try:
            parser.read()          # performs the GET for you
            self._robots_parser = parser
        except Exception as e:
            print(f'Could not read robots.txt ({e}); assuming allowed')
            self._robots_parser = None

    def _is_allowed_by_robots(self) -> bool:
        if not self._robots_parser:
            return True
        path = self.url.replace('/'.join(self.url.split('/')[:3]) + '/', '', 1)
        return self._robots_parser.can_fetch('*', path)


    def scrape(self, selector: str):
        """
        Return the *text* of the first element that matches `selector`.
        If nothing is found, returns `None`.
        """
        soup = BeautifulSoup(self._html, 'html.parser')
        elem = soup.select_one(selector)
        return elem.get_text(strip=True) if elem else None
