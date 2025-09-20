from fastapi import APIRouter, HTTPException
from typing import List, Optional

# Pydantic models
from app.models.webpage import WebpageCreate, WebpageInDB
from app.models.scrape import ScrapeInDB
from app.models.scrape_data import ScrapeData

# Helpers
from app.utils import get_aiomysql_connection, execute_mysql_query

router = APIRouter(prefix="/webpages", tags=["webpages"])


################ Helper functions ################

async def _fetch_all_webpages() -> List[dict]:
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT webpage_id, url, page_name
              FROM webpages
           ORDER BY webpage_id;
        """
        return await execute_mysql_query(conn, query)


async def _fetch_webpage_by_id(webpage_id: int) -> Optional[dict]:
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT webpage_id, url, page_name
              FROM webpages
             WHERE webpage_id = %s;
        """
        rows = await execute_mysql_query(conn, query, (webpage_id,))
        return rows[0] if rows else None


async def _create_webpage(data: WebpageCreate) -> int:
    async with get_aiomysql_connection() as conn:
        query = """
            INSERT INTO webpages (url, page_name)
            VALUES (%s, %s);
        """
        last_id = await execute_mysql_query(
            conn,
            query,
            params=(data.url, data.page_name),
            return_lastrowid=True
        )
        return last_id


async def _update_webpage(webpage_id: int, data: WebpageCreate) -> bool:
    async with get_aiomysql_connection() as conn:
        query = """
            UPDATE webpages
               SET url = %s,
                   page_name = %s
             WHERE webpage_id = %s;
        """
        rowcount = await execute_mysql_query(
            conn,
            query,
            params=(data.url, data.page_name, webpage_id),
            return_rowcount=True
        )
        return rowcount > 0


async def _delete_webpage(webpage_id: int) -> bool:
    async with get_aiomysql_connection() as conn:
        query = """
            DELETE FROM webpages WHERE webpage_id = %s;
        """
        rowcount = await execute_mysql_query(
            conn,
            query,
            params=(webpage_id,),
            return_rowcount=True
        )
        return rowcount > 0


async def _fetch_scrapes_by_webpage(webpage_id: int) -> List[dict]:
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT scrape_id, locator, metric_name
              FROM scrapes
             WHERE webpage_id = %s
           ORDER BY scrape_id;
        """
        return await execute_mysql_query(conn, query, (webpage_id,))


async def _fetch_scrape_data_by_webpage(webpage_id: int) -> List[dict]:
    async with get_aiomysql_connection() as conn:
        # Join all three tables to pull the data you want
        query = """
            SELECT sd.data_id,
                   sd.scrape_id,
                   sd.value,
                   sd.datetime
              FROM scrape_data AS sd
              JOIN scrapes AS s ON sd.scrape_id = s.scrape_id
             WHERE s.webpage_id = %s
           ORDER BY sd.datetime DESC;
        """
        return await execute_mysql_query(conn, query, (webpage_id,))


################ Endpoints ################

@router.get("/", response_model=List[WebpageInDB])
async def get_webpages():
    """
    Return an array of all webpages stored in the system.
    """
    rows = await _fetch_all_webpages()
    return rows


@router.post(
    "/", status_code=201, response_model=WebpageInDB
)
async def create_webpage(page: WebpageCreate):
    """
    Create a new webpage record.

    The URL must be unique - the database will raise an error if it already exists.
    """
    try:
        last_id = await _create_webpage(page)
    except Exception as exc:
        # Most likely a duplicate key violation
        raise HTTPException(status_code=400, detail=str(exc))

    new_record = await _fetch_webpage_by_id(last_id)
    return new_record


@router.get("/{id}", response_model=WebpageInDB)
async def get_webpage(id: int):
    """
    Return the single webpage with that ID.
    """
    row = await _fetch_webpage_by_id(id)
    if not row:
        raise HTTPException(status_code=404, detail="Webpage not found")
    return row


@router.put("/{id}", response_model=WebpageInDB)
async def replace_webpage(id: int, page: WebpageCreate):
    """
    Replace an existing webpage (full update).
    """
    success = await _update_webpage(id, page)
    if not success:
        raise HTTPException(status_code=404, detail="Webpage not found")

    updated_record = await _fetch_webpage_by_id(id)
    return updated_record


@router.patch("/{id}", response_model=WebpageInDB)
async def patch_webpage(id: int, page: WebpageCreate):
    """
    Patch an existing webpage - only the fields you send will be updated.
    """
    # Build a dynamic query
    updates = []
    params = []

    if page.url is not None:
        updates.append("url = %s")
        params.append(page.url)
    if page.page_name is not None:
        updates.append("page_name = %s")
        params.append(page.page_name)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    async with get_aiomysql_connection() as conn:
        query = f"""
            UPDATE webpages
               SET {', '.join(updates)}
             WHERE webpage_id = %s;
        """
        params.append(id)
        rowcount = await execute_mysql_query(
            conn,
            query,
            params=params,
            return_rowcount=True
        )
        if rowcount == 0:
            raise HTTPException(status_code=404, detail="Webpage not found")

    return await _fetch_webpage_by_id(id)


@router.delete("/{id}")
async def delete_webpage(id: int):
    """
    Remove the webpage - all associated scrapes and data are deleted automatically via FK cascade.
    """
    success = await _delete_webpage(id)
    if not success:
        raise HTTPException(status_code=404, detail="Webpage not found")
    return {"msg": "Webpage deleted"}


@router.get("/{id}/scrapes", response_model=List[ScrapeInDB])
async def get_webpage_scrapes(id: int):
    """
    Return all scrapes defined for a given webpage.
    """
    # Make sure the webpage exists first
    if not await _fetch_webpage_by_id(id):
        raise HTTPException(status_code=404, detail="Webpage not found")

    rows = await _fetch_scrapes_by_webpage(id)
    return rows


@router.get("/{id}/scrapes/data", response_model=List[ScrapeData])
async def get_webpage_scrape_data(id: int):
    """
    Return all scraped data points for a given webpage.
    """
    if not await _fetch_webpage_by_id(id):
        raise HTTPException(status_code=404, detail="Webpage not found")

    rows = await _fetch_scrape_data_by_webpage(id)
    return rows
