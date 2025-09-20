# webpages/routers.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_webpages():
    '''
    Return an array of all webpages
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.post("/")
def post_webpages():
    '''
    Create a new webpage record.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/{id}")
def get_webpage(id: int):
    '''
    Return the single webpage with that ID.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.put("/{id}")
def put_webpage(id: int):
    '''
    Replace or patch the webpage (full update).
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.delete("/{id}")
def delete_webpage(id: int):
    '''
    Remove the webpage - all associated scrapes and data are deleted automatically via FK cascade.
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/{id}/scrapes")
def get_webpage(id: int):
    '''
    Return the scrapes of a webpage
    '''
    return { 'msg': 'Yet to be implemented.' }


@router.get("/{id}/scrapes/data")
def get_webpage(id: int):
    '''
    Return the data that has been scraped from a webpage
    '''
    return { 'msg': 'Yet to be implemented.' }
