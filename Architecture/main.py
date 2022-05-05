"""
Here is where you import and use the class FastAPI, tying everything together.

You don't have to worry about performance when including routers. This will take
microseconds and will only happen at startup, thereby not affecting performance.
"""

from fastapi import FastAPI,Depends
from dependedncies import get_query_token,get_token_header
from routers import items, users,auth
from internal import admin
from routers.auth import not_authenticated_exception_handler,NotAuthenticatedException,manager



app=FastAPI() #Global dependencies

app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418:{"description":"I am a teapot"}}
    )
app.include_router(auth.router)

manager.not_authenticated_exception = NotAuthenticatedException
app.add_exception_handler(NotAuthenticatedException, not_authenticated_exception_handler)

