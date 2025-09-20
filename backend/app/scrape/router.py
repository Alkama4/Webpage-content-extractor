# scrape/routers.py
from fastapi import APIRouter
from app.utils import get_aiomysql_connection, execute_mysql_query

router = APIRouter()

@router.get("/")
async def get_scrape_data():
    '''
    Retrieve scraped data
    '''
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT *
            FROM scrape_data
        """
        scrape_data = await execute_mysql_query(conn, query)

        return { "data": scrape_data }
    
@router.post("/")
async def run_scrape():
    '''
    Run the scraping script
    '''
    async with get_aiomysql_connection() as conn:
        query = """
            SELECT 
                w.webpage_id, w.url, w.page_name,
                s.scrape_id, s.locator, s.metric_name
            FROM webpages w
            LEFT JOIN scrapes s ON w.webpage_id = s.webpage_id;
        """
        rows = await execute_mysql_query(conn, query)

        # Group by webpage
        webpages = {}
        for r in rows:
            wid = r['webpage_id']
            if wid not in webpages:
                webpages[wid] = {
                    "webpage_id": wid,
                    "url": r['url'],
                    "page_name": r['page_name'],
                    "scrapes": []
                }
            if r['scrape_id']:
                webpages[wid]["scrapes"].append({
                    "scrape_id": r['scrape_id'],
                    "locator": r['locator'],
                    "metric_name": r['metric_name']
                })

        # Scraping action for the webpages

        return list(webpages.values())
