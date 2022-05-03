from fastapi import FastAPI,Request,Depends,status,Form
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse,Response
from fastapi_login import LoginManager
import os
from dotenv import load_dotenv
from db import users
from utils import get_hashed_password,verify_password
from datetime import timedelta
from schema import UserIn, UserDB

#Basic config
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv()
templates = Jinja2Templates(directory=BASEDIR+"/templates")


#initialization of application
app = FastAPI()


manager = LoginManager(secret="SECRET",token_url='/login',use_cookie=True)
manager.cookie_name="AUTH"  #This is given in Request.cookies : dict
@manager.user_loader() #How are you going to load a user object?
def user_loader(username):
    if username in users:
        return UserDB(**users[username])


@app.get(path="/login",response_class=HTMLResponse)
def login_page(request:Request):
    return templates.TemplateResponse('login.html',{"request":request,"title":"AUTH - Login"},status_code=200)

@app.post(path='/login',response_class=Response)
def login(request: Request,user_info:OAuth2PasswordRequestForm = Depends()):
    username = user_info.username
    password = user_info.password
    
    #User validation
    if username not in users or not verify_password(password,users[username].get("hashed_password")): 
        return templates.TemplateResponse("login.html",{"request":request,"title":"AUTH - Login","invalid":False})
    
    #Token generation
    token = manager.create_access_token(data={"sub":username},expires=timedelta(minutes=30))
    resp = RedirectResponse('/',status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,token)
    return resp


@app.get('/protected')
def protected(user =Depends(manager)):
    return {"a":"b"}


@app.get('/logout')
def logout(user =Depends(manager)):
    resp = RedirectResponse('/',status_code=status.HTTP_302_FOUND)
    manager.set_cookie(response=resp,token=None)
    return resp



@app.post('/register')
def registration(request:Request,password:str=Form(...),user:UserIn=Depends(UserIn.as_form)):
    hashed_password = get_hashed_password(password)
    
    invalid=False
    #Check if username is already taken
    for db_name in users.keys():
        if user.name == db_name :
            invalid = True
    if invalid:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    users[user.name] = jsonable_encoder(UserDB(**user.dict(),hashed_password=hashed_password))
    resp = RedirectResponse('/login',status_code=status.HTTP_302_FOUND)
    return resp

@app.get(path='/')
def index():
    return {"msg":"Hello World"}