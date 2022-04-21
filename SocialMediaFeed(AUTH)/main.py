from fastapi import FastAPI, Request,Response,Depends,status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List,Optional
from passlib.context import CryptContext
from fastapi_login import LoginManager
import os
from dotenv import load_dotenv
from db import users
from datetime import timedelta


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
    
    
#env variables
load_dotenv(dotenv_path='./')
SECRET = os.getenv("SECRET_KEY")

ACCESS_TOKEN_EXPIRES_MINUTES=60 

#passwordhashing 
pwd_ctx = CryptContext(schemes=["bcrypt"])
def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password,hashed_password)


#login - global variable
manager = LoginManager(secret=SECRET,token_url="/login",use_cookie=True)
manager.cookie_name="auth"

@manager.user_loader()
def get_user_from_db(username:str):
    if username in users.key():
        return UserDB(**users[username])

def authenticate_user(username:str,password:str):
    user=get_user_from_db(username=username)
    if not user:
        return None
    if not verify_password(plain_password=password,hashed_password=user.hashed_password)
        return None
    return user




#Initialization of application
app = FastAPI()

#Templates
templates= Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")





#Now we're going to create Database Model inheriting not from BaseModel but from our pydantic model
class UserDB(User):
    hashed_password:str #1

@app.get('/', response_class=HTMLResponse)
def root(request:Request):
    return templates.TemplateResponse("index.html",{"request":request,"title":"FriendConnect - Home"})


@app.get("/login",response_class=HTMLResponse)
def get_login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request,"title":"FriendConnect - Login"})



@app.post("/login") 
def login(request:Request,response:Response,form_data:OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)) :
    user = authenticate_user(username=form_data.username,password=form_data.password)
    if not user: 
        return templates.TemplateResponse("login.html",{"request":request,"title":"FriendConnect - Login","invalid":True},status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES) 
    access_token = manager.create_access_token(data={"sub":user.username},expires=access_token_expires) #2
    
    resp = RedirectResponse("/home",status_code=status.HTTP_302_FOUND)
    
