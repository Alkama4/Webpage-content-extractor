from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List, Optional

# Pydantic models
from app.models.scrape import ScrapeCreate, ScrapeInDB
from app.models.scrape_data import ScrapeData

# Project utils
from app.utils import get_aiomysql_connection, execute_mysql_query
from app.scraper.utils import group_scrapes_by_webpage, run_scrapes_by_webpage

router = APIRouter(prefix="/scrapes", tags=["scrapes"])


#######################  Helper functions #######################

async def _fetch_all_scrapes() -> List[dict]:
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT scrape_id, locator, metric_name, webpage_id
            FROM scrapes
            ORDER BY scrape_id;
        """
        return await execute_mysql_query(conn, query)


async def _fetch_scrape_by_id(scrape_id: int) -> Optional[dict]:
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT scrape_id, locator, metric_name, webpage_id
            FROM scrapes
            WHERE scrape_id = %s;
        """
        rows = await execute_mysql_query(conn, query, (scrape_id,))
        return rows[0] if rows else None


async def _create_scrape(data: ScrapeCreate, webpage_id: int) -> int:
    async with get_aiomysql_connection() as conn:
        query = """
            INSERT INTO scrapes (locator, metric_name, webpage_id)
            VALUES (%s, %s, %s);
        """
        last_id = await execute_mysql_query(
            conn,
            query,
            params=(data.locator, data.metric_name, webpage_id),
            return_lastrowid=True
        )
        return last_id


async def _update_scrape(scrape_id: int, data: ScrapeCreate) -> bool:
    async with get_aiomysql_connection() as conn:
        query = """
            UPDATE scrapes
            SET locator = %s,
                metric_name = %s
            WHERE scrape_id = %s;
        """
        rowcount = await execute_mysql_query(
            conn,
            query,
            params=(data.locator, data.metric_name, scrape_id),
            return_rowcount=True
        )
        return rowcount > 0


async def _delete_scrape(scrape_id: int) -> bool:
    async with get_aiomysql_connection() as conn:
        query = """
            DELETE FROM scrapes WHERE scrape_id = %s;
        """
        rowcount = await execute_mysql_query(
            conn,
            query,
            params=(scrape_id,),
            return_rowcount=True
        )
        return rowcount > 0


async def _fetch_scrape_data_by_scrape(scrape_id: int) -> List[dict]:
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT data_id, scrape_id, value, created_at
            FROM scrape_data
            WHERE scrape_id = %s
            ORDER BY created_at;
        """
        return await execute_mysql_query(conn, query, (scrape_id,))


async def _fetch_all_webpage_and_scrape_rows() -> List[Dict[str, Any]]:
    """
    Return a list of rows that contain both webpage and scrape columns.
    Each row is a plain dict (column name -> value).
    """
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT
                w.webpage_id, w.url, w.page_name,
                s.scrape_id, s.locator, s.metric_name
            FROM webpages AS w
            LEFT JOIN scrapes AS s ON w.webpage_id = s.webpage_id;
        """
        return await execute_mysql_query(conn, query)


async def _persist_scraped_data(scrape_data: List[Dict[str, Any]]) -> None:
    """
    Bulk-insert the scraped values. Returns the number of rows inserted.
    Uses a single INSERT statement with many VALUES tuples for speed.
    """
    if not scrape_data:
        return

    async with get_aiomysql_connection() as conn:

        # Build placeholders: "(%s, %s), (%s, %s), ..."
        values_placeholder = ", ".join(["(%s, %s)"] * len(scrape_data))
        query = f"""
            INSERT INTO scrape_data (scrape_id, value)
            VALUES {values_placeholder};
        """

        # Flatten the list of tuples into a single tuple for executemany
        params: List[Any] = []
        for row in scrape_data:
            params.extend([row.scrape_id, row.value])

        await execute_mysql_query(
            conn,
            query,
            tuple(params),
            return_rowcount=True,
        )



########################  Endpoints  ########################

@router.get("/", response_model=List[ScrapeInDB])
async def get_scrapes():
    """Return an array of all scrape jobs."""
    rows = await _fetch_all_scrapes()
    return rows


@router.post("/run-all")
async def run_all_scrapes():
    """
    Trigger the nightly batch that iterates over every scrape job and runs them. Returns the count of scraped values.
    """
    # Get all scrapes joined with webpages
    rows = await _fetch_all_webpage_and_scrape_rows()

    # Group by webpage (returns List[WebPageWithScrapes])
    grouped = group_scrapes_by_webpage(rows)

    # Run the scraper
    results = run_scrapes_by_webpage(grouped)

    # Persist data to the db
    await _persist_scraped_data(results)

    return {"message": "Scraping completed", "scrape_count": len(results)}


@router.post("/{webpage_id}", status_code=201, response_model=ScrapeInDB)
async def create_scrape(page_id: int, scrape: ScrapeCreate):
    """
    Create a new scrape job for the given webpage.
    The `webpage_id` must exist - MySQL will raise an FK error otherwise.
    """
    try:
        last_id = await _create_scrape(scrape, page_id)
    except Exception as exc:
        # Likely a foreign‑key or duplicate key violation
        raise HTTPException(status_code=400, detail=str(exc))

    new_record = await _fetch_scrape_by_id(last_id)
    return new_record


@router.get("/{scrape_id}", response_model=ScrapeInDB)
async def get_scrape(scrape_id: int):
    """Return the single scrape with that ID."""
    row = await _fetch_scrape_by_id(scrape_id)
    if not row:
        raise HTTPException(status_code=404, detail="Scrape not found")
    return row


@router.put("/{scrape_id}", response_model=ScrapeInDB)
async def replace_scrape(scrape_id: int, scrape: ScrapeCreate):
    """Replace an existing scrape (full update)."""
    success = await _update_scrape(scrape_id, scrape)
    if not success:
        raise HTTPException(status_code=404, detail="Scrape not found")

    updated_record = await _fetch_scrape_by_id(scrape_id)
    return updated_record


@router.patch("/{scrape_id}", response_model=ScrapeInDB)
async def patch_scrape(scrape_id: int, scrape: ScrapeCreate):
    """
    Patch an existing scrape - only the fields you send will be updated.
    """
    # Build a dynamic query
    updates = []
    params = []

    if scrape.locator is not None:
        updates.append("locator = %s")
        params.append(scrape.locator)
    if scrape.metric_name is not None:
        updates.append("metric_name = %s")
        params.append(scrape.metric_name)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    async with get_aiomysql_connection() as conn:
        query = f"""
            UPDATE scrapes
            SET {', '.join(updates)}
            WHERE scrape_id = %s;
        """
        params.append(scrape_id)
        rowcount = await execute_mysql_query(
            conn,
            query,
            params=params,
            return_rowcount=True
        )
        if rowcount == 0:
            raise HTTPException(status_code=404, detail="Scrape not found")

    return await _fetch_scrape_by_id(scrape_id)


@router.delete("/{scrape_id}")
async def delete_scrape(scrape_id: int):
    """Delete the scrape - its data is removed via FK cascade."""
    success = await _delete_scrape(scrape_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scrape not found")
    return {"msg": "Scrape deleted"}


@router.get("/{scrape_id}/data", response_model=List[ScrapeData])
async def get_scrape_data(scrape_id: int):
    """Retrieve all data points for a particular scrape."""
    # Ensure the scrape exists first
    if not await _fetch_scrape_by_id(scrape_id):
        raise HTTPException(status_code=404, detail="Scrape not found")

    rows = await _fetch_scrape_data_by_scrape(scrape_id)
    return rows
