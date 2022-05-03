"""
APIRouter

Path operations related to your users.
You can think of APIRoter as a mini FastAPI class.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get('/users', tags=["users"])  
async def read_users():
    return [{"username":"Migo"},{"username":"Morty"}]

@router.get('/users/me',tags=['users'])
async def read_user_me():
    return {"username":"current_user"}

@router.get("/users/{username}",tags=["users"])
async def read_user(username:str):
    return {"username":username}

