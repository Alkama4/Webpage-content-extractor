# scrapes/routers.py
from fastapi import APIRouter
from app.utils import get_aiomysql_connection, execute_mysql_query

router = APIRouter()

@router.get("/")
async def get_scrapes():
    '''
    List all scrape jobs
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.post("/")
def create_scrape():
    '''
    Create a new scrape job
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/data")
def get_all_scrape_data():
    '''
    Retrieve all of the scraped data.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.post("/run-all")
async def run_all_scrapes():
    '''
    Trigger the nightly batch that iterates over every scrape job and runs them.
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


@router.get("/{id}")
def get_scrape(id: int):
    '''
    List the details of a scrape
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.put("/{id}")
def update_scrape(id: int):
    '''
    Update the given scrape
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.put("/{id}")
def delete_scrape(id: int):
    '''
    Update the given scrape
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.delete("/{id}")
def delete_scrape(id: int):
    '''
    Delete the scrape with its scrape_id. Assosiated data is deleted via cascade.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.post("/{id}/run")
def run_scrape(id: int):
    '''
    Execute the scraper for this job once, store a new row in scrape_data.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/{id}/data")
def run_scrape(id: int):
    '''
    Retrieve the data acquired form a certain scrape.
    '''
    return { 'msg': 'Yet to be implemented.' }
