from fastapi import APIRouter, HTTPException
from typing import List, Optional, Tuple, Any
from aiomysql import Connection

# Pydantic models
from app.models.webpage import WebpageCreate, WebpageInDB, WebpagePatch, WebpageOut
from app.models.element import ElementInDB
from app.models.element_data import ElementData

# Project utils
from app.utils import get_aiomysql_connection, execute_mysql_query
from app.lifespan import scheduler_manager

router = APIRouter(prefix="/webpages", tags=["webpages"])


################ Helper functions ################

async def _fetch_all_webpages(conn: Connection) -> List[dict]:
    query = """
        SELECT webpage_id, url, page_name, run_time, is_enabled
        FROM webpages
        ORDER BY webpage_id;
    """
    return await execute_mysql_query(conn, query)


async def _fetch_webpage_by_id(conn: Connection, webpage_id: int) -> Optional[dict]:
    query = """
        SELECT webpage_id, url, page_name, run_time, is_enabled
        FROM webpages
        WHERE webpage_id = %s;
    """
    rows = await execute_mysql_query(conn, query, (webpage_id,))
    return rows[0] if rows else None


async def _create_webpage(conn: Connection, data: WebpageCreate) -> int:
    query = """
        INSERT INTO webpages (url, page_name, run_time, is_enabled)
        VALUES (%s, %s, %s, %s, %s);
    """
    try:
        last_id = await execute_mysql_query(
            conn,
            query,
            params=(data.url, data.page_name, data.run_time, data.is_enabled),
            return_lastrowid=True
        )
        return last_id
    except Exception as exc:
        # MySQL error 1062 => duplicate entry for unique key
        if hasattr(exc, "args") and len(exc.args) > 0 and "1062" in str(exc.args[0]):
            raise HTTPException(
                status_code=409, 
                detail={
                    "detail": "URL must be unique",
                    "field": "url",
                    "value": data.url
                }
            )
        raise  # re‑raise any other exception unchanged


async def _update_webpage_helper(
    conn: Connection,
    webpage_id: int,
    fields: List[Tuple[str, Any]]
) -> Tuple[int, Optional[dict]]:
    """
    Update a webpage with the supplied list of (column, value) tuples.
    Raises:
        HTTPException 409 if the new URL already exists for another record.
    Returns:
        rowcount, updated record (or None if not found)
    """
    # Check for duplicate URL before updating
    url_field = next((val for col, val in fields if col == "url"), None)
    if url_field is not None:
        dup_q = """
            SELECT 1 FROM webpages
            WHERE url = %s AND webpage_id <> %s
            LIMIT 1;
        """
        dup_res = await execute_mysql_query(
            conn,
            dup_q,
            params=[url_field, webpage_id]
        )
        if dup_res:
            # URL already exists for another record – abort update
            raise HTTPException(
                status_code=409, 
                detail={
                    "detail": "URL must be unique",
                    "field": "url",
                    "value": str(url_field)
                }
            )

    updates = [f"{col} = %s" for col, _ in fields]
    params = [val for _, val in fields]
    params.append(webpage_id)

    query = f"""
        UPDATE webpages
        SET {', '.join(updates)}
        WHERE webpage_id = %s;
    """

    rowcount = await execute_mysql_query(
        conn,
        query,
        params=params,
        return_rowcount=True
    )

    if rowcount == 0:
        exists_q = "SELECT 1 FROM webpages WHERE webpage_id = %s"
        result = await execute_mysql_query(
            conn,
            exists_q,
            params=[webpage_id]
        )
        if not result:      # truly missing
            return 0, None

    updated_record = await _fetch_webpage_by_id(conn, webpage_id)
    return rowcount, updated_record


async def _delete_webpage(conn: Connection, webpage_id: int) -> bool:
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


async def _fetch_elements_by_webpage(conn: Connection, webpage_id: int) -> List[dict]:
    query = """
        SELECT webpage_id, element_id, locator, metric_name
        FROM elements
        WHERE webpage_id = %s
        ORDER BY element_id;
    """
    return await execute_mysql_query(conn, query, (webpage_id,))


async def _fetch_element_data_by_webpage(conn: Connection, webpage_id: int) -> List[dict]:
    # Join all three tables to pull the data you want
    query = """
        SELECT sd.data_id,
                sd.element_id,
                sd.value,
                sd.created_at
        FROM element_data AS sd
        JOIN elements AS s ON sd.element_id = s.element_id
        WHERE s.webpage_id = %s
        ORDER BY sd.created_at DESC;
    """
    return await execute_mysql_query(conn, query, (webpage_id,))


################ Endpoints ################

@router.get("/", response_model=List[WebpageInDB])
async def get_webpages():
    """
    Return an array of all webpages stored in the system.
    """
    async with get_aiomysql_connection() as conn:
        rows = await _fetch_all_webpages(conn)
        return rows


@router.post("/", status_code=201, response_model=WebpageInDB)
async def create_webpage(page: WebpageCreate):
    """
    Create a new webpage record.

    The URL must be unique - the database will raise an error if it already exists.
    """
    async with get_aiomysql_connection() as conn:
        last_id = await _create_webpage(conn, page)

        await scheduler_manager.add_schedule(last_id)

        new_record = await _fetch_webpage_by_id(conn, last_id)
        return new_record


@router.get("/{webpage_id}", response_model=WebpageInDB)
async def get_webpage(webpage_id: int):
    """
    Return the single webpage with that webpage_id.
    """
    async with get_aiomysql_connection() as conn:
        row = await _fetch_webpage_by_id(conn, webpage_id)
        if not row:
            raise HTTPException(status_code=404, detail="Webpage not found")
        return WebpageInDB(**row)


@router.put("/{webpage_id}", response_model=WebpageOut)
async def replace_webpage(webpage_id: int, page: WebpageCreate):
    async with get_aiomysql_connection() as conn:
        fields = [
            ("url", page.url),
            ("page_name", page.page_name),
            ("run_time", page.run_time),
            ("is_enabled", page.is_enabled)
        ]
        rowcount, updated_record = await _update_webpage_helper(conn, webpage_id, fields)

        if not updated_record:
            raise HTTPException(status_code=404, detail="Webpage not found")

        await scheduler_manager.update_schedule(webpage_id)

        # Flag is true only if a row was actually changed
        updated_record["updated"] = rowcount > 0
        return updated_record


@router.patch("/{webpage_id}", response_model=WebpageOut)
async def patch_webpage(webpage_id: int, page: WebpagePatch):
    async with get_aiomysql_connection() as conn:
        fields = []
        if page.url is not None:
            fields.append(("url", page.url))
        if page.page_name is not None:
            fields.append(("page_name", page.page_name))
        if page.run_time is not None:
            fields.append(("run_time", page.run_time))
        if page.is_enabled is not None:
            fields.append(("is_enabled", page.is_enabled))

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        rowcount, updated_record = await _update_webpage_helper(conn, webpage_id, fields)

        if not updated_record:
            raise HTTPException(status_code=404, detail="Webpage not found")

        await scheduler_manager.update_schedule(webpage_id)

        # Flag is true only if a row was actually changed
        updated_record["updated"] = rowcount > 0
        return updated_record


@router.delete("/{webpage_id}")
async def delete_webpage(webpage_id: int):
    """
    Remove the webpage - all associated elements and data are deleted automatically via FK cascade.
    """
    async with get_aiomysql_connection() as conn:
        success = await _delete_webpage(conn, webpage_id)
        if not success:
            raise HTTPException(status_code=404, detail="Webpage not found")
        
        await scheduler_manager.remove_schedule(webpage_id)

        return {"msg": "Webpage deleted"}


@router.get("/{webpage_id}/elements", response_model=List[ElementInDB])
async def get_webpage_elements(webpage_id: int):
    """
    Return all elements defined for a given webpage.
    """
    async with get_aiomysql_connection() as conn:
        # Make sure the webpage exists first
        if not await _fetch_webpage_by_id(conn, webpage_id):
            raise HTTPException(status_code=404, detail="Webpage not found")

        rows = await _fetch_elements_by_webpage(conn, webpage_id)
        return rows


@router.get("/{webpage_id}/elements/data", response_model=List[ElementData])
async def get_webpage_element_data(webpage_id: int):
    """
    Return all elementd data points for a given webpage.
    """
    async with get_aiomysql_connection() as conn:
        if not await _fetch_webpage_by_id(conn, webpage_id):
            raise HTTPException(status_code=404, detail="Webpage not found")

        rows = await _fetch_element_data_by_webpage(conn, webpage_id)
        return rows
