## Project introduction
This project focuses primarily on authentication:
- password hashing
- JWT
- user Authentication
- cookies
<br>

But also, I'll be covering:
- how to use environment variable
- user input validation

### Setting up app
1. For login mechanism:
```
pip install fastapi-login
```

2. For password hashing:
```
pip install "passlib[bcrypt]"
```

3. For environment variable:
```
pip install python-dotenv
```

### Creating app
```
mkdir templates
mkdir static
touch main.py
```

### Initializing application
***main.py:***
```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates= Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"),name="static")


@app.get('/')
def root():
    return {"Set":"Up"}
```

### Creating models 
It is a bad idea to store passwords in plain text in databases.<br>
Password hashing is taking whatever the password and encrypts it using complex algorithm that cannot be reversed.<br><br>

```python
from pydantic import BaseModel
from typing import List, Optional
from db import users

class Notification(BaseModel):
    author: str
    description: str

class User(BaseModel):
    name: str
    username: str
    email: str
    birthday: str
    friends: List[str]
    notifications: List[Notification]

#Now we're going to create Database Model inheriting not from BaseModel but from our pydantic model
class UserDB(User):
    hashed_password:str #1


```
1. Why hashed_password is specially treated being used only in UserDB? Because we don't want to include passwords out to the users even if they're hashed, for security purposes. 



### Creating base home page
templates/header.html:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <link rel="stylesheet" href="{{url_for('static',path='/style.css')}}">
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title | default("Page")}}</title>
</head>
<body>
```
<br>

templates/footer.html:
```html
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
</body>
</html>
```
<br>

templates/navbar.html:
```html
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
        <!-- navbar-brand class is applied to typical branding logo you see in the top navigation bar -->
        <a class="navbar-brand" href="/">FriendConnect</a> 

        <!-- The data-bs-target attribute accepts a CSS selector to apply the collapse to -->
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>

        
        <div class="navbar navbar-collapse" id="navbarSupportedContent"> 
            <ul class="navbar-nav me-auto mb-lg-0">
                <li class="nav-item">
                    <a class="nav-link" href="/home">Home</a>
                </li>
            </ul>
            <ul class="navbar-nav d-flex justify-content-end"> <!-- End of the navbar-->
                <li class="nav-item">
                    <a class="nav-link" href="/login">Login</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/Register">Register</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/logout">Logout</a>
                </li>
            </ul>

        </div>

    </div>
</nav>
```
<br>

templates/index.html
```html
{% include 'header.html' %}
{% include 'navbar.html' %}

<div class="container" style="width: 100%; margin: 1em auto; text-align: center;">
    <h1>Welcome to FriendConnect</h1>
    <p>This site aims to connect friends with friends. Register or log in to start!</p>
</div>
{% include 'footer.html' %}

```
<br>

**main.py**
```python
from fastapi.responses import HTMLResponse
from fastapi import Request #1
@app.get('/', response_class=HTMLResponse)
def root(request:Request):
    return templates.TemplateResponse("index.html",{"request":request,"title":"FriendConnect - Home"})

```
1. Again, if you want to render HTML to users, you must pass in the key-value pair that includes Request object in template response.


### Creating Login page
templates/login.html:
```html
{% include 'header.html' %}
{% include 'navbar.html' %}
<style>
    .container{
        margin-top: 1em;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }

</style>
<div class="container">
    <form action="/login" method="POST">
        <div class="mb-3"> <!--One for the Username-->
            <label for="username" class="form-label">Username</label>
            <input type="text" class="form-control" id="username" name="username" required> <!-- so we don't send empty data to backend-->
        </div>
        <div class="mb-3"> <!--One for the Password-->
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" name="password" required> <!-- so we don't send empty data to backend-->
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
</div>
{% include 'footer.html' %}
```
<br>

main.py:
```python
@app.get("/login",response_class=HTMLResponse)
def get_login(request:Request):
    return templates.TemplateResponse("login.html",{"request":request,"title":"FriendConnect - Login"})
```

#### Adding invalid message
Using if statement in Jinja2, the template can tract a variable called "invalid" and if the value is true, it's just going to display red paragraph that is going to say "invalid username(or password)"<br><br>

templates/login.html:
```html
...
    <div class="mb-3"> <!--One for the Password-->
            <label for="password" class="form-label">Password</label>
            <input type="text" class="form-control" id="password" name="password" required> <!-- so we don't send empty data to backend-->
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    {% if invalid %}
        <p style="margin-top:0.5em; color: #eb4823">Invalid username or password. Please try again.</p>
    {% endif %}
</div>
```

If you want to test this out at this point, you can just pass in "invalid" key with argument True in '/login' endpoint.



### Mechanism of Password hashing
Most web developers and security experts use what is called password hashing,<br>
which is using some encryption method to scramble up the password.<br><br>

Leaving aside how the algorithm works, the point is it returns a string that is UNIQUE to the password,<br>
but CANNOT be reversed. With that anti-reversal property, this works in a way that:
- user passes in real(orginal) password
- server generates the hashed_password based on the given password
- server matches if the hashed_password is the same as the one in the Database.
<br>

As a logical consequence, we need: 
- password hashing function - which will take a plaintext password from the user
- password verifying function 

```python
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"],deprecated="auto") #1

def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password,hashed_password)

print(get_hashed_password("password")) #2 #$2b$12$vrq3SSTFi/5IGR1G.lBINu7RDt3UebXxcMjQQxVYpD5/IsHe6LtE2
print(get_hashed_password("password")) #3 #$2b$12$gmJxB6tb5JAJozlmZfRiyeM1bOaXaPChfQBgMY4Po7hImfzsnNrpm
print(verify_password("password",get_hashed_password("password"))) #4 True
```
1. 'schemes' is to specify the type of hashing mechanism we want
2. As you can see, even with the same password, the return values of hashed_password are different.
3. However, even though the yielded hashed password look different, within the scheme we specify, **they're treated as the same password**, hence the possibility of verification of password. 
4. In real example, you would need to load the hash_password from DB.


### Login mechanism : User verification
We're going to be using an external library called fastapi_login; otherwise you have to work with native fastapi code and that's mouthful.<br>
```python
from fastapi_login import LoginManager

manager= LoginManger(secret='.',token_url="/login", use_cookie=True) #1 #2 #3 #4 #5

```
1. This instance takes in 3 arguments. 
    - secrets : string that is used to encrypt our token
    - token_url : the url we are going to get the token from (this is going to be POST request)
    - use_cookie(optional) : this allows us to use cookies to store our tokens so that the users don't have to send headers over all the time.
<br>

2. All of the authorization works through **JWT**; a way of taking a bunch of data and turning it into one long string to identify user.
<br>

3. The token is sent using either 
    - HTTP headers : posted in requests 
    - or through cookies : it store token to a permanent piece of information in web browser and on any website you visit you can access that cookie to see if the user is authorized.
<br>

4. The token has information about the user, username, the time that we want the token to last for, and some other general information. 
<br>

5. JWT is NOT **hashed** or **encrypted**. They can be easily reversed if you have the secret key. But we don't have to worry about it because the only way you use the secret key is to verify the user. Plus, the only reason or the only way we would generate the key is after we complete all of the user authentication with the hashed passwords. 
<br>

#### Using environment variable
As you may have remembered, we've installed python-dotenv. 
```python
>>> import os
>>> os.urandom(24).hex() #generate random key
```
```sh
touch .env
vi .env

#.env
SECERET_KEY="value from the generated key above"
```

```python
from fastapi_login import LoginManager
import os
from dotenv import load_dotenv #1
load_dotenv() #1
SECRET_KEY=os.getenv("SECRET_KEY") #2
ACCESS_TOKEN_EXPIRES_MINUTES=60 #3

manager= LoginManger(secret=SECRET__KEY,token_url="/login", use_cookie=True) 
manager.cookie_name = "auth" #4
```
1. This is going to allow us to import all of our environment variables from the files into Python namespace
2. Now we can actually get env varaibles.
3. To build in some general expiry time for web tokens so we don't allow attackers to have indefinite access. This will be used when we're actually creating the token
4. Set the name of cookie that's used for our token.


#### User authentication
We need two functions:
- one for getting the user from the DB with ogin manager's decorator function. 
- one for authentication function that will take, in a plaintext, username and password.

```python
manager= LoginManger(secret=SECRET__KEY,token_url="/login", use_cookie=True) 
manager.cookie_name = "auth"

@manager.user_loader() #4
def get_user_from_db(username:str):
    if username in users.keys(): #1
        return UserDB(**users[username])

def authenticate_user(username:str, password:str):
    user= get_user_from_db(username=username)
    if not user:
        return None
    if not verify_password(plain_password=password,hashed_password=user.hashed_password) #2
        return None
    return user #3
```
1. This must be modified when you actually work with database. 
2. we specified this in the model(UserDB)
3. If the function returns user, it indicates the user is authenticated.
4. This assign the function below to the manager so when it's going through authentication on the pages, it's going to use this to get the user from the DB. (So, basically this is to define how a user is loaded.)


### Login Mechanism : Login data route
We are going to complete our login mechanism by creaing the login endpoint.<br>
If the user isn't authenticated, we'll be redirecting the request to the endpoint.<br>

```python
from fastapi import Request, Response, Depends #3
from fastapi.security import OAuth2PasswordRequestForm
@app.post("/login") #1
def login(request:Request,response:Response,form_data:OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)): #2
    pass
 
```
<br><br>

**What is OAuth?**<br>
Before OAuth, sites would prompt you to enter your username and password directly into a form and they would log in to your data (e.g. your Gmail account) as you.<br>
This is often called the password anti-pattern.<br><br>

To create a better system for the web, federated identity was created for single sign-on (SSO).<br>
In this scenario, an end user talks to their identity provider, and the identity provider generates a cryptographically signed token<br>
which it hands off to the application to authenticate the user. <br><br>

OAuth is a delegated authorization framework for REST/APIs.<br>
It enables apps to obtain limited access (scopes) to a user’s data without giving away a user’s password.<br><br>

You can think of this like hotel key cards, but for apps. <br>
If you have a hotel key card, you can get access to your room.<br> 
How do you get a hotel key card? <br>
You have to do an authentication process at the front desk to get it.<br><br>

To break it down simply, OAuth is where:<br>
- App requests authorization from User.
- User authorizes App and delivers proof.
- App presents proof of authorization to server to get a Token.
- Token is restricted to only access what the User authorized for the specific App.


1. This is where our form is redirecting
2. We need three main argument here.
    - **Request** : if the user isn't authenticated, we want to redirect back to login page. And Request object is required for HTML response.
    - **Response Object**: to allow or attach the cookie to our response.
    - **form data** : through OAuth2PasswordRequestForm, it will contain username and password. 

3. **Depends** : For easy use of dependency injection. This is useful when you need to have shared logic, database connections, enforce security, authentication, role requirements and so on.<br> 

#### Closer look at Depends()
**functions as dependencies** <br>
For example:
```python
from fastapi import Depends
from typing import Optional
async def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons
```
With two lines, it has teh same shape and structure that all your path operation functions have.<br>
In this case, this dependency expects:
- An optional query parameter q that is a 'str'
- An optional query parameter skip that is an 'int', and by default is 0.
- An optional query parameter limit that is an 'int', and by default is 100.
So the parameter passed in must be callables like function and that function takes parameters in the same way that path operation functions do.<br><br>

**classes as dependencies** <br>
The key factor is that a dependency should be a "callable".<br>
A "callable" in Python is anything that Python can "call" like a function.<br>
You might notice that to create an instance of a Python class, you use that same syntax.
```python
class Cat:
    def __init__(self, name:str):
        self.name =name

fluffy = Cat(name="Mr Fluffy")
```
To create fluffy, you "called" Cat. So, a Python class is also a callable.<br>
If you pass a "callable" as a dependency in FastAPI, it will analyze the parameters for that "callable",<br> 
and process them in the same way as the parameters for a path operation function.<br><br>

For example:
```python
from typing import Optional
from fastapi import Depends, FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
```



<br><br>

#### Back to main topic - access token

Now, we have our three main parameters working, let's actually get started. 
```python
from fastapi import Request, Response, Depends 
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

@app.post("/login") 
def login(request:Request,response:Response,form_data:OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    user=authenticate_user(username=form_data.username,password=form_data.password)
    if not user: #1
        return templates.TemplateResponse("login.html",{"request":request,"title":"FriendConnect - Login","invalid":True},status_code=status.HTML_401_UNAUTHORIZED)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES) 
    access_token = manager.create_access_token(data={"sub":user.username},expires=access_token_expires) #2
 
```
1. If you cannot find a user from DB
2. If everything goes well, we will create access token using login manager variable. First thing we want to pass in is data we want to encode into the token for which in this case we have 'sub' 
<br><br>

Now we have created our access token and now that's incorporated into our library and we don't need to handle any of the complex parts of the token.<br><br>

Now we have access token, we need to work with the response and set the cookie.

#### response and cookie
```python

@app.post("/login") 
def login(request:Request,response:Response,form_data:OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    user=authenticate_user(username=form_data.username,password=form_data.password)
    if not user: 
        return templates.TemplateResponse("login.html",{"request":request,"title":"FriendConnect - Login","invalid":True},status_code=status.HTML_401_UNAUTHORIZED)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES) 
    access_token = manager.create_access_token(data={"sub":user.username},expires=access_token_expires) #2
    
    resp = RedirectResponse("/home",status_code=status.HTTP_302_FOUND) 
    manager.set_cookie(resp, access_token) #1
    return resp #2

```
1. Firstly, you add response and next we put access token that contains username data and expiration time. 
2. The return value is resp, NOT cookie, which makes sense as cookie is set using the "Set-Cookie" header field sent in an HTTP response from the web server. This header field instructs the web browser to store the cookie and send it back in future requests to the server. 

### Exception handling

```python 

class NotAuthenticatedException(Exception):
    pass

def not_authenticated_exception_handler(req,except): #5
    return RedirectResponse("/login")

manager.not_authenticated_exception = NotAuthenticatedException #3
app.add_exception_handler(NotAuthenticatedException, not_authenticated_exception_handler) #4
@app.get('/home')
def home(user:User = Depends(manager)): #1 #2
    return user

```
1. User is depending on manager. When you do this, you have it depend on variable, and it's going to call the variable and do all of the deep authentication work that the login manager has done for us. 

2. By default it will raise an exception in JSON saying,
```
{"detail":"Not authenticated"}
```
SO you can confirm that by making user "Depends" on "manager", <br>
if necessitates login

3. You specify how you want the login manager handles not authenticated access. In this example, we use custom exception. 

4. Only with custom exception though, you can't necessitate user logging in. You have to map the exception to function. So when a certain exception occurs, that is mapped to the function and within the function, we put redirection logic.

5. Note too that the function being mapped to must have two parameter, each of which is for **'request'** and **'exception'**, respectively.

Let's boot up the screen and click the 'home', you'll be redirected to login page.<br>
Just a heads-up that password for the user here is 'password'


### Logout mechanism
Just like we set the cookie, if you set the cookie to remove the token, it's the very logout mechanism. 

```python
@app.get('/logout',response_class=RedirectResponse)
def logout(): #1
    response = RedirectResponse('/')
    manager.set_cookie(response, None) #2
    return response

```
1. This isn't going to take any parameters 
2. Unlike before when we set the cookie with access_token, this time we set cookie to None, effectively removing existing cookie; therefore no more authentication.



### Registration Page
#### Frontend part
```python
@app.get('/register',response_class=HTMLResponse)
def get_register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request,"title":"FriendConnect - Register","invalid":False})
```
<br>

**register.html**:
```html
{% include 'header.html' %}
{% include 'navbar.html' %}
<div class="container" style="justify-self: center;">
    <form action="/register" method="POST">
        <div class="mb-3">
            <label for="username" class="form-label"></label>
            <input type="text" class="form-control" id="username" name="username">
        </div>
        <div class="mb-3">
            <label for="email" class="form-label"></label>
            <input type="email" class="form-control" id="email" name="email">
        </div>
        <div class="mb-3">
            <label for="name" class="form-label"></label>
            <input type="text" class="form-control" id="name" name="name">
        </div>
        <div class="mb-3">
            <label for="password" class="form-label"></label>
            <input type="password" class="form-control" id="password" name="password">
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
    {% if invalid %}
        <p style="margin-top: 0.5em; color: #eb4823">This user is already registered.</p>
    {% endif %}
</div>
{% include 'footer.html' %}

```

#### BackEnd Part