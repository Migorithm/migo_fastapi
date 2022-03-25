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
we want to make it so that the use can input only specific parts of the Car.<br><br>
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