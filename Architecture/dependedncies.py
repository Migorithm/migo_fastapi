"""
Here, I'm using an invented header to simplify the example.
"""

from fastapi import Header,HTTPException

async def get_token_header(x_token:str = Header(...)):
    if x_token != "fake-user-secret-token":
        raise HTTPException(status_code=400,detail="X-Token header invalid")
    
async def get_query_token(token:str):
    if token != "migo":
        raise HTTPException(status_code=400, detail="No Migo token provided")