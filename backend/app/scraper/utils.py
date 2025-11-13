from typing import Any, Dict, List, Optional
from aiomysql import Connection
from pydantic import BaseModel, HttpUrl, Field
import re
from decimal import Decimal
from app.scraper.web_page_scraper import WebPageScraper
from app.scraper.BrowserFetcher import BrowserFetcher
from app.utils import get_aiomysql_connection, execute_mysql_query
from .ErrorClasses import ElementNotFoundError
from collections import defaultdict

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

class ValidationRequest(BaseModel):
    """Request payload for validating elements on a single page."""
    url: HttpUrl = Field(..., description="The full URL that will be elementd")
    locators: list[str]

class ValidationResult(BaseModel):
    locator: str
    value: float | None

class ValidationData(ValidationRequest):
    locators: list[ValidationResult]


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


def _group_elements_by_webpage(rows: List[Dict]) -> List[PageWithElements]:
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


async def _run_scrapes_by_webpage(conn: Connection, webpages: List[PageWithElements]) -> List[ScrapeResult]:
    results: List[ScrapeResult] = []
    fetcher = BrowserFetcher()
    await fetcher.start()
    scraper = WebPageScraper(fetcher)

    for page in webpages:
        try:
            await scraper.load(page.url)
        except Exception as exc:
            webpage_log_id = await _initialize_webpage_log(conn, page.webpage_id)
            await _finalize_webpage_log(conn, webpage_log_id, "failure", f"Page load failed: {exc}")
            continue

        webpage_log_id = await _initialize_webpage_log(conn, page.webpage_id)
        webpage_status = "success"
        error_groups: dict[str, list[int]] = defaultdict(list)

        for element in page.elements:
            try:
                raw_value = scraper.scrape(element.locator)
                numeric = parse_number(raw_value)
                results.append(ScrapeResult(element_id=element.element_id, value=numeric))
                await _insert_element_log(conn, webpage_log_id, element.element_id, "success", "Scraped successfully")
            except ElementNotFoundError as e:
                error_groups["ElementNotFoundError"].append(element.element_id)
                await _insert_element_log(conn, webpage_log_id, element.element_id, "failure", str(e))
                webpage_status = "partial"
            except ValueError as e:
                error_groups["ValueError"].append(element.element_id)
                await _insert_element_log(conn, webpage_log_id, element.element_id, "failure", str(e))
                webpage_status = "partial"
            except Exception as exc:
                error_groups["UnexpectedError"].append(element.element_id)
                await _insert_element_log(conn, webpage_log_id, element.element_id, "failure", f"Unexpected error: {exc}")
                webpage_status = "partial"

        if error_groups:
            # Build a concise summary like "ValueError for elements 4,5; ElementNotFoundError for 6,7"
            message = "; ".join(
                f"{err} for element {ids[0]}" if len(ids) == 1 else f"{err} for elements {', '.join(map(str, ids))}"
                for err, ids in error_groups.items()
            )
        else:
            message = "Scraped successfully"

        await _finalize_webpage_log(conn, webpage_log_id, webpage_status, message)

    await fetcher.stop()
    return results


async def _fetch_all_webpage_and_element_rows(conn: Connection) -> List[Dict[str, Any]]:
    query = """
        SELECT
            w.webpage_id, w.url, w.page_name,
            s.element_id, s.locator, s.metric_name
        FROM webpages AS w
        LEFT JOIN elements AS s ON w.webpage_id = s.webpage_id
        WHERE w.is_enabled = TRUE;
    """
    return await execute_mysql_query(conn, query)


async def _fetch_webpage_and_elements_by_id(
    conn: Connection,
    webpage_id: int,
    ignore_is_enabled: bool
) -> List[Dict[str, Any]]:
    if ignore_is_enabled:
        query = """
            SELECT
                w.webpage_id, w.url, w.page_name,
                s.element_id, s.locator, s.metric_name
            FROM webpages AS w
            LEFT JOIN elements AS s ON w.webpage_id = s.webpage_id
            WHERE w.webpage_id = %s;
        """
    else:
        query = """
            SELECT
                w.webpage_id, w.url, w.page_name,
                s.element_id, s.locator, s.metric_name
            FROM webpages AS w
            LEFT JOIN elements AS s ON w.webpage_id = s.webpage_id
            WHERE w.webpage_id = %s AND w.is_enabled = TRUE;
        """
    return await execute_mysql_query(conn, query, (webpage_id,))


async def _persist_element_data(conn: Connection, element_data: List[ScrapeResult]) -> None:
    if not element_data:
        return

    placeholders = ", ".join(["(%s, %s)"] * len(element_data))
    query = f"INSERT INTO element_data (element_id, value) VALUES {placeholders};"
    params: List[Any] = []
    for row in element_data:
        params.extend([row.element_id, row.value])

    await execute_mysql_query(conn, query, tuple(params), return_rowcount=True)


async def _initialize_webpage_log(
    conn: Connection,
    webpage_id: int,
    message: str = "Scrape ran into an unexpected error and did not finish gracefully."
) -> int:
    """
    Inserts a new webpage log with status 'running' and returns its ID.
    """
    query = """
        INSERT INTO webpage_logs (webpage_id, status, message)
        VALUES (%s, %s, %s);
    """
    return await execute_mysql_query(conn, query, (webpage_id, "partial", message), return_lastrowid=True)


async def _finalize_webpage_log(
    conn: Connection,
    webpage_log_id: int,
    status: str,
    message: str
) -> None:
    """
    Updates a webpage log with its final status and summary message.
    """
    query = """
        UPDATE webpage_logs
        SET status=%s, message=%s
        WHERE webpage_log_id=%s;
    """
    await execute_mysql_query(conn, query, (status, message, webpage_log_id))


async def _insert_element_log(conn, webpage_log_id: int, element_id: int, status: str, message: str):
    query = """
        INSERT INTO element_logs (webpage_log_id, element_id, status, message)
        VALUES (%s, %s, %s, %s);
    """
    await execute_mysql_query(conn, query, (webpage_log_id, element_id, status, message))


async def run_scrape(
    webpage_id: int | None = None, 
    ignore_is_enabled: bool = False,
) -> str:
    """
    Runs scrapes for either all active webpages or a single one if `webpage_id` is provided.
    Uses shared scraper utils for grouping, scraping, and persistence.
    """
    async with get_aiomysql_connection() as conn:
        if webpage_id:
            rows = await _fetch_webpage_and_elements_by_id(conn, webpage_id, ignore_is_enabled)
        else:
            rows = await _fetch_all_webpage_and_element_rows(conn)

        webpages = _group_elements_by_webpage(rows)
        results = await _run_scrapes_by_webpage(conn, webpages)
        await _persist_element_data(conn, results)

    scope = f"webpage_id={webpage_id}" if webpage_id else "all active webpages"
    return f"Scrape completed for {scope}"
