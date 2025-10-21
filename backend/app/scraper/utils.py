from typing import Any, Dict, List, Optional
from .web_page_scraper import WebPageScraper
from pydantic import BaseModel, HttpUrl, Field
import re
from decimal import Decimal
from fastapi import HTTPException
from app.utils import get_aiomysql_connection, execute_mysql_query

class ElementInfo(BaseModel):
    element_id: int
    locator: str
    metric_name: Optional[str] = None

class PageWithElements(BaseModel):
    webpage_id: int
    url: str
    page_name: str | None = None
    elements: List[ElementInfo]

class ScrapeResult(BaseModel):
    element_id: int
    value: float | None

class ValidateRequest(BaseModel):
    """Request payload for validating elements on a single page."""
    url: HttpUrl = Field(..., description="The full URL that will be elementd")
    locators: list[str]

class ValidateResult(BaseModel):
    locator: str
    value: float | None

class ValidationData(ValidateRequest):
    locators: list[ValidateResult]


def group_elements_by_webpage(rows: List[Dict]) -> List[PageWithElements]:
    """
    Turn a flat list of (webpage + element) rows into a nested structure
    grouped by `webpage_id`. Missing elements (rows where `element_id` is None)
    are ignored.
    """
    pages: Dict[int, PageWithElements] = {}

    for r in rows:
        wid = r["webpage_id"]
        page = pages.setdefault(
            wid,
            PageWithElements(
                webpage_id=wid,
                url=r["url"],
                page_name=r.get("page_name"),
                elements=[],
            ),
        )

        # Only add a element if the id is not NULL
        if r["element_id"] is not None:
            # Build a ElementInfo instance instead of a plain dict
            page.elements.append(
                ElementInfo(
                    element_id=r["element_id"],
                    locator=r["locator"],
                    metric_name=r.get("metric_name"),
                )
            )

    return list(pages.values())


def run_scrapes_by_webpage(webpages: List[PageWithElements]) -> List[ScrapeResult]:
    """
    Execute the scraper for every element listed under each webpage.
    Returns a flat list of dicts: {element_id, value}.
    """
    results: List[ScrapeResult] = []

    for page in webpages:
        scraper = WebPageScraper(page.url)

        for element in page.elements:
            try:
                raw_value = scraper.scrape(element.locator)
            except Exception as exc:
                print(f"Failed on {page.webpage_id} / {element.element_id}: {exc}")
                continue

            if raw_value is None:
                continue

            try:
                numeric = parse_number(raw_value)
            except ValueError as exc:
                print(f"Could not parse value for {page.webpage_id} / {element.element_id}: {exc}")
                continue

            results.append(ScrapeResult(element_id=element.element_id, value=numeric))

    return results


def validate_scrapes(req: ValidateRequest) -> List[ValidateResult]:
    """
    Work-horse for the `/validate` endpoint.

    Parameters
    ----------
    req : ValidateRequest
        The request payload containing a single URL and a list of CSS/XPath locators.
    Returns
    -------
    List[ValidateResult]
        A flat list of `{scrape_id, value}` objects.  `scrape_id` is set to ``0`` because
        the validation step does not correspond to an actual database record.
    """
    results: List[ValidateResult] = []

    # Instantiate a scraper for the given URL once and reuse it for all locators
    scraper = WebPageScraper(str(req.url))

    for idx, locator in enumerate(req.locators):
        try:
            raw_value = scraper.scrape(locator)
        except Exception as exc:      # pragma: no cover - debugging helper
            print(f"Failed to scrape locator {locator!r}: {exc}")
            continue

        if raw_value is None:
            continue

        try:
            numeric = parse_number(raw_value, allow_percent=False, force_decimal=True)
        except ValueError as exc:     # pragma: no cover - debugging helper
            print(f"Could not parse value for locator {locator!r}: {exc}")
            raise HTTPException(
                status_code=400, 
                detail={
                    "detail": "A scraped elements value couldn't be converted to a number.",
                    "field": "locator",
                    "type": "value_error",
                    "locator": locator,
                    "value": raw_value
                }
            )

        results.append(ValidateResult(locator=locator, value=numeric))

    return ValidationData(url=req.url, locators=results)


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


async def _fetch_all_webpage_and_element_rows(conn) -> List[Dict[str, Any]]:
    query = """
        SELECT
            w.webpage_id, w.url, w.page_name,
            s.element_id, s.locator, s.metric_name
        FROM webpages AS w
        LEFT JOIN elements AS s ON w.webpage_id = s.webpage_id
        WHERE w.is_active = TRUE;
    """
    return await execute_mysql_query(conn, query)


async def _fetch_webpage_and_elements_by_id(conn, webpage_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT
            w.webpage_id, w.url, w.page_name,
            s.element_id, s.locator, s.metric_name
        FROM webpages AS w
        LEFT JOIN elements AS s ON w.webpage_id = s.webpage_id
        WHERE w.webpage_id = %s AND w.is_active = TRUE;
    """
    return await execute_mysql_query(conn, query, (webpage_id,))


async def _persist_element_data(conn, element_data: List[ScrapeResult]) -> None:
    if not element_data:
        return

    placeholders = ", ".join(["(%s, %s)"] * len(element_data))
    query = f"INSERT INTO element_data (element_id, value) VALUES {placeholders};"
    params: List[Any] = []
    for row in element_data:
        params.extend([row.element_id, row.value])

    await execute_mysql_query(conn, query, tuple(params), return_rowcount=True)


async def run_scrape(webpage_id: int | None = None) -> str:
    """
    Runs scrapes for either all active webpages or a single one if `webpage_id` is provided.
    Uses shared scraper utils for grouping, scraping, and persistence.
    """
    async with get_aiomysql_connection() as conn:
        if webpage_id:
            rows = await _fetch_webpage_and_elements_by_id(conn, webpage_id)
        else:
            rows = await _fetch_all_webpage_and_element_rows(conn)

        webpages = group_elements_by_webpage(rows)
        results = run_scrapes_by_webpage(webpages)
        await _persist_element_data(conn, results)

    scope = f"webpage_id={webpage_id}" if webpage_id else "all active webpages"
    return f"Scrape completed for {scope}"
