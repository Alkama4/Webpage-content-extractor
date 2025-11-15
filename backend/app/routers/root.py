from typing import List
from aiomysql import Connection
from fastapi import APIRouter, Response
from app.utils import get_aiomysql_connection, execute_mysql_query
from app.scraper.utils import run_scrape
from app.scraper.BrowserFetcher import BrowserFetcher

router = APIRouter(prefix="", tags=["root"])

@router.get("/")
def root():
    """
    Basic landing endpoint. Visit the API docs at /docs or /redoc.
    """
    return {"msg": "Hello world! See /docs for interactive documentation."}


@router.get("/preview")
async def preview(url: str):
    fetcher = BrowserFetcher()
    await fetcher.start()
    
    try:
        html = await fetcher.fetch(url)
    except PermissionError:
        return Response(content="Blocked by robots.txt", status_code=403)
    finally:
        await fetcher.stop()

    return Response(content=html, media_type="text/html")


@router.post("/run_active_scrapes")
async def run_active_scrapes():
    """
    Scrape all of the active webpages.
    """
    await run_scrape()
    return {
        "msg": "Scrapes completed for active webpages.",
    }


@router.get("/logs")
async def get_logs():
    """
    Get the logs.
    """
    async with get_aiomysql_connection() as conn:
        rows = await _fetch_logs(conn)
        return rows



####################### Helpers #######################

async def _fetch_logs(conn: Connection) -> List[dict]:
    query = """
        SELECT 
            wl.webpage_log_id,
            wl.webpage_id,
            w.page_name,
            wl.attempted_at AS webpage_attempted_at,
            wl.status AS webpage_status,
            wl.message AS webpage_message,

            el.element_log_id,
            el.element_id,
            e.metric_name,
            el.attempted_at AS element_attempted_at,
            el.status AS element_status,
            el.message AS element_message

        FROM webpage_logs wl
        JOIN webpages w ON wl.webpage_id = w.webpage_id
        LEFT JOIN element_logs el ON wl.webpage_log_id = el.webpage_log_id
        LEFT JOIN elements e ON el.element_id = e.element_id
        ORDER BY wl.attempted_at DESC, el.attempted_at ASC;
    """

    rows = await execute_mysql_query(conn, query)

    grouped = {}
    for row in rows:
        wid = row["webpage_log_id"]
        if wid not in grouped:
            grouped[wid] = {
                "webpage_log_id": wid,
                "webpage_id": row["webpage_id"],
                "page_name": row["page_name"],
                "attempted_at": row["webpage_attempted_at"],
                "status": row["webpage_status"],
                "message": row["webpage_message"],
                "elements": []
            }

        if row["element_log_id"]:
            grouped[wid]["elements"].append({
                "element_log_id": row["element_log_id"],
                "element_id": row["element_id"],
                "metric_name": row["metric_name"],
                "attempted_at": row["element_attempted_at"],
                "status": row["element_status"],
                "message": row["element_message"]
            })
    
    for entry in grouped.values():
        entry["elements"].sort(key=lambda x: x["element_id"] or 0)

    return list(grouped.values())
