from datetime import timedelta
from models.database import users
from passlib.context import CryptContext
from fastapi import APIRouter,Depends,HTTPException ,Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from schemas import UserDB
from fastapi_login import LoginManager
import os 



pwd_ctx = CryptContext(schemes=["bcrypt"])

def get_hashed_password(plain_password:str):
    return pwd_ctx.hash(plain_password)

def verify_password(plain_password,hashed_password):
    return pwd_ctx.verify(plain_password,hashed_password)

def authenticate_user(username:str,password:str):
    if username not in users:
        return False
    return verify_password(password,users[username].get("hashed_password"))


#
manager = LoginManager(os.urandom(24).hex(),token_url="/login",use_cookie=True)
manager.cookie_name ="Auth"
@manager.user_loader()
def user_loader(username):
    if username in users:
        return UserDB(**users[username])
    
class NotAuthenticatedException(Exception):
    pass
def not_authenticated_exception_handler(req:Request,exce):
    return RedirectResponse("/login")


#Router

router = APIRouter(
    prefix="/login",
    tags = ["login"]
)

@router.get('/')
def login_page():
    return {"Okay!":"Login page!"}

@router.post('/')
def login(user_info: OAuth2PasswordRequestForm = Depends()):
    print("dssd")

    if not authenticate_user(user_info.username, user_info.password):
        raise HTTPException(status_code=404,detail="User Not Found")
    token = manager.create_access_token(data={"sub":user_info.username},expires=timedelta(minutes=30))
    response = RedirectResponse("/login",status_code=302)
    manager.set_cookie(response,token=token)
    return response