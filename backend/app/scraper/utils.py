from typing import Dict, List, Optional
from .web_page_scraper import WebPageScraper
from pydantic import BaseModel
import re
from decimal import Decimal

class ScrapeInfo(BaseModel):
    scrape_id: int
    locator: str
    metric_name: Optional[str] = None

class PageWithScrapes(BaseModel):
    webpage_id: int
    url: str
    page_name: str | None = None
    scrapes: List[ScrapeInfo]

class ScrapeResult(BaseModel):
    scrape_id: int
    value: float | None


def group_scrapes_by_webpage(rows: List[Dict]) -> List[PageWithScrapes]:
    """
    Turn a flat list of (webpage + scrape) rows into a nested structure
    grouped by `webpage_id`. Missing scrapes (rows where `scrape_id` is None)
    are ignored.
    """
    pages: Dict[int, PageWithScrapes] = {}

    for r in rows:
        wid = r["webpage_id"]
        page = pages.setdefault(
            wid,
            PageWithScrapes(
                webpage_id=wid,
                url=r["url"],
                page_name=r.get("page_name"),
                scrapes=[],
            ),
        )

        # Only add a scrape if the id is not NULL
        if r["scrape_id"] is not None:
            # Build a ScrapeInfo instance instead of a plain dict
            page.scrapes.append(
                ScrapeInfo(
                    scrape_id=r["scrape_id"],
                    locator=r["locator"],
                    metric_name=r.get("metric_name"),
                )
            )

    return list(pages.values())


def run_scrapes_by_webpage(webpages: List[PageWithScrapes]) -> List[ScrapeResult]:
    """
    Execute the scraper for every scrape listed under each webpage.
    Returns a flat list of dicts: {scrape_id, value}.
    """
    results: List[ScrapeResult] = []

    for page in webpages:
        scraper = WebPageScraper(page.url)

        for scrape in page.scrapes:
            try:
                raw_value = scraper.scrape(scrape.locator)
            except Exception as exc:
                print(f"Failed on {page.webpage_id} / {scrape.scrape_id}: {exc}")
                continue

            if raw_value is None:
                continue

            try:
                numeric = parse_number(raw_value)
            except ValueError as exc:
                print(f"Could not parse value for {page.webpage_id} / {scrape.scrape_id}: {exc}")
                continue

            results.append(ScrapeResult(scrape_id=scrape.scrape_id, value=numeric))

    return results


def parse_number(raw: str,
                 allow_percent: bool = False,
                 force_decimal: bool = True) -> float:
    """
    Convert an arbitrary numeric string to a Python float.

    Parameters
    ----------
    raw : str
        The scraped value, e.g. "$2 684,00", "1 234.56", "-12%".
    allow_percent : bool, default False
        If True, a trailing '%' is interpreted as a percentage (i.e. 0.12).
    force_decimal : bool, default True
        When True the result will always be a float (Decimal → float).  
        Set to False if you want to keep Decimal for exact math.

    Returns
    -------
    float
        The numeric value.

    Raises
    ------
    ValueError
        If no numeric component can be extracted.
    """
    # Trim whitespace
    s = raw.strip()

    # Detect and handle percent sign if requested
    percent_multiplier = 1.0
    if allow_percent and s.endswith('%'):
        percent_multiplier = 0.01
        s = s[:-1]          # drop the %

    # Remove any leading currency symbol(s) or other non‑numeric chars.
    #    We keep digits, commas, dots, spaces, plus/minus signs.
    cleaned = re.sub(r'[^\d.,+\- ]', '', s)

    # Replace common thousands separators with nothing
    #    (comma in US/UK, space or dot in many European locales)
    cleaned = cleaned.replace(' ', '').replace(',', '')

    # If a dot remains but we are sure the locale uses comma as decimal,
    #    you might need to swap it. Here we assume '.' is always decimal.
    if not cleaned:
        raise ValueError(f"Could not parse numeric value from '{raw}'")

    try:
        number = Decimal(cleaned)
    except Exception as exc:
        raise ValueError(f"Failed to convert '{cleaned}' to Decimal: {exc}") from exc

    # Apply percent multiplier
    number *= Decimal(percent_multiplier)

    return float(number) if force_decimal else number
