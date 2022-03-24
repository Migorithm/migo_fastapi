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
