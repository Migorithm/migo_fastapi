## FirstStep to FastAPI

### Installation
```sh
pip install fastapi
pip install uvicorn
```

### Constrcution of route
```python
from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def root():
    return {"Hi!":"Welcome to FastAPI"}
```


### Run application
```sh
#simple run
uvicorn python\_file\_without\_.py:application_variable

#exapmle
uvicorn main:app

#--reload for live update
uvicorn main:app --reload

```

### Defining model
```python
from pydantic import BaseModel
from typing import Optional,List,Dict
class Car(BaseModel):
    make: str
    model: str
    year: int
    price: float
    engine: Optional[str] = "V4" #Default value
    autonomous: bool
    sold: List[str]
```


#### Field restriction 
Say you don't want any car older than 1970 or later than the latest. 
```python
from pydantic import BaseModel, Field
from typing import Optional,List
class Car(BaseModel):
    make: str
    model: str

    #First argument is going to be default value. If you don't want, put "..." 
    year: int = Field(...,ge=1970,lt=2022) 

    price: float
    engine: Optional[str] = "V4" #Default value
    autonomous: bool
    sold: List[str]

```

### Response hint & query string
```python
from fastapi import FastAPI, Query  #for query string
@app.get('/cars',response_model=List[Dict[str,Car]]) 
def get_cars(number:Optional[str] = Query("10",max_length=3)): #max_length 3will restrict the range of query up to 999
    response = []
    for id, car in list(cars.items())[:int(number)]: #To take queried amount of car 
        to_add ={}
        to_add[id] = car
        response.append(to_add)
    return response
```
Wait, you may be curious at this point how you can define query string.<br>
Unlike Flask, you need "Query" moduel from fastapi.<br>
You pass in argument name first which is in this case "number" and say that's equal to **Query**.<br>
If you pass in '...' in Query, it means the Query string is "required"<br>
Otherwise, any parameter passed in will be set as the default. <br><br>

Furthermore, if you want to put default value it comes first. But notice that it's string.<br>
Lastly, max_length will decide the length of the string. In this case, if you want the query<br>
to be no more than 3 digit value(up to 999), it should be just 3(not 999!)


### Getting specific car by ID
```python
from fastapi import Path, HTTPException , status

@app.get("/cars/{id}",response_model=Car)
def get_car_by_id(id:int = Path(...,ge=0,lt=1000)):
    car = cars.get(id)
    if not car:
        raise HTTPException(status_code=404,detail="Could not find car by ID.")
        #Or you can
        #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Whatever you want to say")
    return car

```
Just like we did with Pydantic models, we can add the same numeric validations to Path or Query. 

#### Difference between Query and Path
Take this URL for example:<br>

    https://stackoverflow.com/questions/tagged/fastapi?sort=Newest&uqlId=26120

Here:
- stackoverflow.com -> domain
- /questions -> Path
- /tagged -> Path
- /fastapi -> Path param.
- sort=Newest -> Query Param.
- uqlId=26120 -> Query Param.
<br>

In in the example above, it's right to put Path as opposed to Query. 

### Post route
In HTTP, you can actually use the same route if it's different method.
```python
@app.get("/cars/{id}",response_model=Car)
def get_car_by_id(id:int = Path(...,ge=0,lt=1000)):
    car = cars.get(id)
    if not car:
        raise HTTPException(status_code=404,detail="Could not find car by ID.")
    return car


from fastapi import status, Body, HTTPException
@app.post("/cars",status_code=status.HTTP_201_CREATED) #define the default status code
def add_cars(body_cars: List[Car], min_id:Optional[int] = Body(0)): #min_id is for offset
    if len(body_cars) < 1:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,detail="No cars to add")
    min_id = len(body_cars.values()) + min_id
    for car in body_cars :
        while cars.get(min_id): #Don't wanna add a car that already exists in the database
            min_id+=1
        cars[min_id] = car
        min_id +=1 

```
One important thing to note here is the **cars** variable is going to be go through the request body.<br>
<br>
If you need to add some singular value to request body, we need to specify it by using **Body** module. <br><br>

We can't actually make post request as yet. But what's really cool about FastAPI is that you can always use<br>
"docs" to fiddle with that. (http://127.0.0.1:8000/docs)<br><br>

The actual post form will be as follows.

    curl -X 'POST' \
    'http://127.0.0.1:8000/cars' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "body_cars": [ 
        {
        "make": "string",
        "model": "string",
        "year": 1980,
        "price": 30.30,
        "engine": "V8",
        "autonomous": true,
        "sold": [
            "NA","SA"
        ]
        }
    ],
    "min_id": 0
    }'


### Updating car
How can you update stuff?<br>
First thing you need to do is actually adjust your "Car" model to make everything optional.<br>
Why? because when we are getting the data from update operation,<br>
we want to make it so that the user can input only specific parts of the Car.<br><br>
```python
from fastapi import FastAPI, HTTPException,status
from pydantic import BaseModel, Field
from typing import Optional,List,Dict
from fastapi.encoder import jsonable_encoder
class Car(BaseModel):
    make: Optional[str]
    model: Optional[str]
    year: Optional[int] = Field(...,ge=1970,lt=2022)
    price: Optional[float]
    engine : Optional[str] = "V4"
    autonomous: Optional[bool]
    sold : Optional[List[str]]

@app.put("/cars/{id}", response_model=Dict[str,Car])
def update_car(id: int, car:Car= Body(...) ): #1
    stored = cars.get(id)
    if not stored:
        raise HTTPException(status_code =status.HTTP_404_NOT_FOUND,detail="Couldn't find car with given ID" )
    stored = Car(**stored) #2
    print(type(car)) #3
    new = car.dict(exclude_unset=True) #4
    new = stored.copy(update=new)
    cars[id] = jsonable_encoder(new) #5
    response ={}
    response[id] = cars[id]
    return response



```
1. Because id is already passed, we don't have to specify Path this time. But if you need validation, you will have to use Path. 
2. Already stored one.
3. You can check the type of car variable you get from request. It's 'main.Car'. This indicates that every request is automatically mapped to pydantic model.
4. this is going to be converted into dictionary. **exclude_unset** set to True will exclude anything that wasn't changed. Note that .dict() and .copy() is basically class method inherited from pydantic's BaseModel.  
5. You cannot pass a pedantic model into the things that we want to do. What **jsonable_encoder** does is basically take whatever you have like **pydantic models** or things that typically can't be stored in a dictionary. 


### Deleting Car
```python
@app.delete("/cars/{id}")
def delete_car(id:int):
    if not cars.get(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find car with given id")

    del cars[id]

```


## Frontend side
Until this point, we've been returning JSON in our argument. That works, but in order to have a frontend with fastAPI, we need to start returning HTML templates. FastAPI can utilize Jinja2. And the way it works is it has a specific directory called **"templates"**. And that is going to contain all of your HTML, and another directory called **static**.

```sh
cd Car_Information_Viewer
mkdir templates
mkdir static
```

```python
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

#1
templates = Jinja2Templates(directory="templates")

#2
app =FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")

```
1. We need to create variable to store Jinja2Templates class object. This will allow us to return a template response and fill in the data with all we need. 
2. Style sheet, CSS files, pictures and so on will be mounted in this way. 
<br><br>

Now, things are ready. Let's go over to templates directory and create a new file called *home.html*<br>
In there, you just press exclamation mark(!) and it will generate html template. Type in whatever you want and go back to:<br>
**main.py**:
```python
#1
from fastapi import Request
from starlette.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)#2
def root(request:Request ):#1
    return templates.TemplateResponse("home.html",{"request":request})
```
1. Note that Request object is passed as argument. Once it's passed, we're actually going to use it when serving up our template. With Request object, you can get:
- client host by - request.client.host
- method type by - request.method 
and so on. <br>
With that though, if you get data from the Request object, it won't be validated, converted or documented by FastAPI.<br>

2. Instead of TemplateResponse, we specify response_class with HTMLResponse. Reason being is editor support and to make sure that no cutting off of data is done. (HTMLResponse is broader class)
<br>

Before we run our application, we actually need to install Jinja2 with pip. 
```sh
pip install jinja2
```

### Using jinja2 template
Use double braces - {{}}:
```python
@app.get('/',response_class=HTMLResponse)
def root(request:Request):
    return templates.TemplateResponse("home.html",{"request":request,"title":"FastAPI - Home"})
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title|default("Document")}}</title> <!-- -->
</head>
<body>
    <h1>Welcome to your first app in FastAPI!</h1>
    
</body>
</html>
```
Note that when you pass in variables and its values, it is wrapped in dictionary but you can directly access them without using "dict["key"]" syntax.<br><br>

Notice too, that {{title | default("Document")}} means that if "title" variable is passed, it will use the value of "title" but if not, it will use default value set to "Document"


### Header & Footer 
We can create basic page every time we need new page.<br>
But what if we need 10 or 20 or 30 pages?<br>
Plus what if we are going to have the same header for all the pages?<br>
Well, actually Jinja allows 
- "include" 
- "extends" 
for the reuse of files. 
<br>

```sh
cd /Car_Information_Viewer/templates
touch header.html
touch footer.html
```
<br><br>

We're going to create header and footer as follows
**header.html**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
``` 
<br>

**footer.html**:
```html
</body>
</html>
```

And let's include bootstrap CDN. 
- CSS : Included right below the head
- JS : Right at the bottom of the body
<br>

**header.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
```
<br>

**footer.html**:
```html
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous">
</body>
</html>
```

What if you want to have separate style sheet?
```html
<link rel="stylesheet" href="{{url_for('static',path='/style.css')}}" type="text/css">
```

### include
Let's use header and footer on our files.<br>
**home.html**:
```html
{% include 'header.html' %}
<h3> Welcome to your first app in FastAPI </h3>
{% include 'footer.html' %}
```


### Navigation bar
Navigation bar contains logo, links, headers, the search bar and so on. Let's create a new html called 'navbar.html'
```sh
touch navbar.html
```

And on Bootstrap website, you can head on over to:

    docs/{version}/components/navbar 
    
for reference.<br>
Example: **navbar.html**
```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container fluid">
            <a class="navbar-brand" href="/cars">CarInformer</a>
        <ul class="navbar-nav me-auto mb-2 mg-lg-0">
            <li class="nav-item">
                <a class="nav-link" href="/create">Create Car</a>
            </li>
        </ul>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse justify-content-end" id="navbarSupportedContent">
            <form action="" class="d-flex" style="margin: 0.5em;">
                <input class="form-control me-2" type="search" placeholder="Get car by ID..." name="id" aria-label="Search">
                <button class="btn btn-outline-light" type="submit">Search</button>
            </form>
        </div>
    </div>
</nav>
```

CSS example: static/style.css
```css
.navbar-brand {
    font-weight: 600;
    font-size: 1.5em;
}

.navbar-dark .navbar-nav .nav-link { /* -- 1 -- */
    color: white;
}
```
1. Why is this long? That's for specificality of identifier. 

### Creating the main page 
currently, we have the following endpoints:
- /
- /cars

For get('/cars') the return value is just List of dictionary.<br> 
```python
@app.get('/cars',response_model=List[Dict[str,Car]])
def get_cars(number:Optional[str] = Query("10",max_length=3)):
    response = []
    for id, car in list(cars.items())[:int(number)]: 
        to_add ={}
        to_add[id] = car
        response.append(to_add)
    return response
```
So we need some changes so it actually returns HTML response.<br>


**/templates/index.html**
```html
{% include 'header.html' %}
{% include 'navbar.html' %}
<p>{{cars}}</p> <!-- Will pass Cars object into this variable-->
{% include 'footer.html' %}
```
```python
@app.get('/cars',response_class=HTMLResponse)
def get_cars(request:Request, number:Optional[str] = Query("10",max_length=3)):
    response = []
    for id, car in list(cars.items())[:int(number)]: 
        to_add ={}
        to_add[id] = car
        response.append(to_add)
    return templates.TemplateReponse("index.html",
        {"request":request,
        "cars":response, #We will pass response to variable(cars)
        "title":"Home"})
```


### Redirect
Redict is a special type of response that's included in fastAPI.<br>
Say the moment any client gets in on the website ('/') and you want to redirect their get request to '/cars'
```python
from fastapi.responses import RedirectResponse
@app.get('/', response_class=RedirectResponse)
def root(request:Request):
    return RedirectResponse(url="/cars")
```
When redirected, your server will log the following:
    
    INFO:     127.0.0.1:64181 - "GET / HTTP/1.1" 307 Temporary Redirect


### Creating Car component
Remember, get('/cars') returns a list of cars. So, we're gonna loop through the list to get a car and display them properly.<br>

template/car.html
```html
<div>
    <h2>{{car["year"]}} {{car["make"]}} {{car["model"]}}</h2>

    <p><strong>Price: {{car["price"]}}$</strong></p>
    <p><strong>{{car["engine"]}}</strong> engine</p>
    {% if car["autonomous"] %}
        <p>This car has autonomous functionality</p>
    {% else %}
        <p>This car <strong>does not have autonomous functionality</strong></p>
    {% endif %}

    {% if car["sold"] %}
        <p>Sold in {{car["sold"]| join(',')}}</p> <!-- build in jinja2 function. And note that key must be double-quoted -->
    {% else %}
        <p>Not currently available.</p>
    {% endif %}
    <p>ID: {{id}}</p>
</div>
```
<br>

templates/index.html
```html
{% include 'header.html' %}
{% include 'navbar.html' %}
<div class="container-fluid">
    {% for id, car in cars %}
        <div class="row justify-content-center" style="text-align: center;"> <!-- To make sure it is centered and vertically aligned -->
            <div class="col col-sm-6" style="border: 1px solid black; margin: 1em 0.5em; border-radius: 10px"> <!-- Oncec it hits the small breakpoint, it will only take up 6 of default 12 given rows in bootstrap  -->
                {% include 'car.html' %}
            </div>
        </div>
    {% endfor %}
</div>

{% include 'footer.html' %}

{% include 'footer.html' %}
```

In order for the loop to work, instead of appending dictionaries, we will turn it into list  of tuple with each item in the list being a tuple of id and the Car. 

```python
@app.get('/cars',response_class=HTMLResponse)
def get_cars(request:Request, number:Optional[str] = Query("10",max_length=3)):
    response = []
    for id, car in list(cars.items())[:int(number)]: 
        response.append(id,car)
    return templates.TemplateResponse("index.html",
        {"request":request,
        "cars":response, #We will pass response to variable(cars)
        "title":"Home"})
```


### Adding a search feature
Let's implement a form into our actual search feature in navigation bar. From there, it's going to send it to a route which we're going to handle through fastAPI.<br><br>

First, we need to implement an "action" and a "method"<br>
templates/navbar.html:
```html
<form action="/search" method="POST" class="d-flex" style="margin: 0.5em;"> <!-- -->
    <input class="form-control me-2" type="search" placeholder="Get car by ID..." name="id" aria-label="Search">
    <button class="btn btn-outline-light" type="submit">Search</button>
</form>
```
The reason we use '/search' is we need to send this data in a request body which then needs to be sent to another URL to display the information. <br><br>

And then let's create a new route to get cars.
```python
from fastapi import Form
@app.post('/search', response_class=RedirectResponse)
def search_cars(id:str=Form(...)) #1
    return RedirectResponse("/cars/" + id, status_code=302) #2

```
1. to get id, we will use form data.
2. We need to pass in a status code. Otherwise, it's going to maintain HTTP method(POST request in this case!). 
<br>

Now we have post route set up and corresponding form. Let's go ahead and create a search page for it to work.<br>
templates/search.html:
```html
{% include 'header.html' %}
{% include 'navbar.html' %}
<div class="container">
    {% if car %}
        {% include 'car.html' %}
    {% else %}
        <h2>Oops! We couldn't find a car with that ID. Please try again.</h2>
    {% endif %}
</div>
{% include 'footer.html' %}
```
<br>

And lastly, We will modify **get('/cars/{id}')** route. 
```python
@app.get("/cars/{id}",response_class=HTMLResponse)
def get_car_by_id(request:Request, id:int = Path(...,ge=0,lt=1000)):
    car = cars.get(id)
    response= templates.TemplateResponse("search.html",{"request":request, "car":car, "id":id,"title":"Search Car"})
    if not car:
        response.status_code = status.HTTP_404_NOT_FOUND #1
    return response
```
1. you can set status_code in this way as well. 


If you want to improve the visualization, go with the following html file.<br>
templates/search.html
```html
{% include 'header.html' %}
{% include 'navbar.html' %}
<style>
    <!-- body {
        width: 100%;
        height: 100vh; 
        display: flex;
        flex-direction: column;
    } -->
    
    #carcon {
        display: flex;
        flex-direction: column;
        text-align: center;
        justify-content: center;
        align-items: center;
        height: 100%;
    }

</style>
<div class="container" id="carcon">
    {% if car %}
        {% include 'car.html' %}
    {% else %}
        <h2>Oops! We couldn't find a car with that ID. Please try again.</h2>
    {% endif %}
</div>
{% include 'footer.html' %}
```

### Creating a car
Let's make a dedicated page which will be linked to '/create' that will send post request to create a car object.<br>
/templates/create.html:
```html
{% include 'header.html' %}
{% include 'navbar.html' %}
<div class="container" style="margin-top: 1em;"> <!-- To make a bit of space-->
    <form action="/cars" method="POST">
        <div class="mb-3">
            <label for="make" class="form-label">Make</label>
            <input type="text" class="form-control" name="make" id="make" aria-describedby="makeDesc">
            <div id="makeDesc" class="form-text">The make of the car</div>
        </div>
        <div class="mb-3">
            <label for="model" class="form-label">Model</label>
            <input type="text" class="form-control" name="model" id="model" aria-describedby="modelDesc">
            <div id="modelDesc" class="form-text">The model of the car</div>
        </div>
        <div class="mb-3">
            <label for="year" class="form-label">Year</label>
            <input type="text" class="form-control" name="year" id="year" aria-describedby="yearDesc">
            <div id="yearDesc" class="form-text">The year of the car</div>
        </div>
        <div class="mb-3">
            <label for="price" class="form-label">price</label>
            <input type="text" class="form-control" name="price" id="price" aria-describedby="priceDesc">
            <div id="priceDesc" class="form-text">The price of the car</div>
        </div>
        <div class="mb-3">
            <label for="engine" class="form-label">Engine</label>
            <input type="text" class="form-control" name="engine" id="engine" aria-describedby="engineDesc">
            <div id="engineDesc" class="form-text">The engine of the car</div>
        </div>

        <!-- Select field --> 
       
        <div class="mb-3">
            <label for="autonomous" class="form-label">Is the car autonomous?</label>
            <select class="form-select" name="autonomous" id="autonomous">
                <option selected value="true">Yes</option>  <!-- converted into boolean by fastapi-->
                <option value="false">No</option>    <!-- boolean -->
            </select>
        </div>

        <!-- Checkbox -->
        <div class="mb-3">
            <p>Where is the car sold?</p>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" name="sold" value="AF">Africa (AF)<br>
                <input class="form-check-input" type="checkbox" name="sold" value="AF">Antarctica (AN)<br>
                <input class="form-check-input" type="checkbox" name="sold" value="AF">Asia (AS)<br>
                <input class="form-check-input" type="checkbox" name="sold" value="AF">Europe (EU)<br>
                <input class="form-check-input" type="checkbox" name="sold" value="AF">North America (NA)<br> 
                <input class="form-check-input" type="checkbox" name="sold" value="AF">Oceania (OC)<br>
                <input class="form-check-input" type="checkbox" name="sold" value="AF">South America (SA)<br>
            </div>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>

</div>

{% include 'footer.html' %}

```
<br>

This form sends the data to the '/cars'. Now, one very important thing we need to keep in mind is we're no longer sending a list of cars or sending body data. We're sending Form data.<br><br>
So you should replace argument that's set to following:

```python
@app.post("/cars",status_code=status.HTTP_201_CREATED) #define the default status code
def add_cars(body_cars: List[Car], min_id:Optional[int] = Body(0)):

```

With the following:
```python
@app.post("/cars",status_code=status.HTTP_201_CREATED) 
def add_cars(
    make:Optional[str] = Form(...),  #1
    model:Optional[str] = Form(...)
    year:Optional[str] = Form(...),
    price:Optional[float] = Form(...),
    engine:Optional[str] = Form(...),
    autonomous:Optional[bool] = Form(...), #4
    sold: Optional[List[str]] = Form(None),  #Default value None. Note that value is obtained from value part of checkbox. 
    min_id:Optional[int] = Body(0)):

    #2
    body_cars = [Car(make=make,model=model,year=year,price=price,engine=engine,autonomous=autonomous,sold=sold)] #Pydantic model

    if len(body_cars) < 1 : 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No cars to add")
    min_id = len(cars.values()) + min_id
    for car in body_cars:
        while cars.get(min_id):
            min_id+=1
        cars[min_id] = car
        min_id+=1
    return RedirectResponse(url="/cars",status_code=302) #3


```
1. Remember, in Pydantic model, (...) indicates a field that is required but can be set to None. Used with Optional it will mean required optional fields. 

2. The last thing we want to do is actually create variables. 

3. It's maintaining HTTP method if you are using default 307 code. In order to have a GET route, we need the 302 tag. 

4. for autonomous=1, True, true, on, yes or any other case variation (uppercase, first letter in uppercase, etc), your function will see the parameter short with a bool value of True. Otherwise as False.