# webpages/routers.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_webpages():
    '''
    Return an array of all webpages
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.post("/")
async def post_webpages():
    '''
    Create a new webpage record.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/{id}")
async def get_webpage(id: int):
    '''
    Return the single webpage with that ID.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.put("/{id}")
async def put_webpage(id: int):
    '''
    Replace or patch the webpage (full update).
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.delete("/{id}")
async def delete_webpage(id: int):
    '''
    Remove the webpage - all associated scrapes and data are deleted automatically via FK cascade.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/{id}/scrapes")
async def get_webpage(id: int):
    '''
    Return the scrapes of a webpage
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/{id}/scrapes/data")
async def get_webpage(id: int):
    '''
    Return the data that has been scraped from a webpage
    '''
    return { 'msg': 'Yet to be implemented.' }
