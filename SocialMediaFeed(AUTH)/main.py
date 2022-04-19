from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List,Optional

app = FastAPI()
templates= Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")

#Model
class Notification(BaseModel):
    auther: str
    description: str

class User(BaseModel):
    name: str
    username: str
    email: str
    birthday: str
    friends: List[str]
    notification: List[Notification]

#Now we're going to create Database Model inheriting not from BaseModel but from our pydantic model
class UserDB(User):
    hashed_password:str #1

@app.get('/', response_class=HTMLResponse)
def root(request:Request):
    return templates.TemplateResponse("index.html",{"request":request,"title":"FriendConnect - Home"})


@app.get("/login",response_class=HTMLResponse)
def get_login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request,"title":"FriendConnect - Login","invalid":True})