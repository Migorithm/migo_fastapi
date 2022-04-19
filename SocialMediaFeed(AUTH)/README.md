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
            <input type="text" class="form-control" id="password" name="password" required> <!-- so we don't send empty data to backend-->
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
        <p style="margin-top:0.5em; color: red">Invalid username or password. Please try again.</p>
    {% endif %}
</div>
```

