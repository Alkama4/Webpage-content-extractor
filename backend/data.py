from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_data():

    # Some logic

    return {
        'values': [1, 2, 3]
    }

@router.get("/website/{website_id}")
def get_data(website_id: int):

    # Some logic

    print(website_id)
    return {
        'website_id': website_id
    }

@router.post("/")
def get_data():

    # Some logic

    return {
        'msg': 'Did that.'
    }
