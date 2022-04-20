from fastapi import FastAPI,Query,Path ,HTTPException,status, Body,Request,Form
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel,Field
from typing import Optional, List,Dict
from starlette.responses import HTMLResponse
from database import cars

class Car(BaseModel):
    make: Optional[str]
    model: Optional[str] 
    year: Optional[int] = Field(...,ge=1970,lt=2022) 

    price: Optional[float]
    engine: Optional[str] = "V4" #Default value
    autonomous: Optional[bool]
    sold: Optional[List[str]]
    
templates = Jinja2Templates(directory="templates") #For serverside rendering1

app = FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static") #For serverside rendering2



@app.get('/',response_class=RedirectResponse)
def root(request:Request):
    
    return RedirectResponse(url="/cars") #url_for?


@app.get('/cars',response_class=HTMLResponse)
def get_cars(request:Request, number:Optional[str] = Query("10",max_length=3)):
    response = []
    for id, car in list(cars.items())[:int(number)]: 
        response.append((id,car))
    return templates.TemplateResponse("index.html",
        {"request":request,
        "cars":response, #We will pass response to variable(cars)
        "title":"Home"})


@app.get("/cars/{id}",response_class=HTMLResponse)
def get_car_by_id(request:Request, id:int = Path(...,ge=0,lt=1000)):
    car = cars.get(id)
    response= templates.TemplateResponse("search.html",{"request":request, "car":car, "id":id,"title":"Search Car"})
    if not car:
        response.status_code = status.HTTP_404_NOT_FOUND #1
    return response

@app.get('/create',response_class=HTMLResponse)
def create_car(request: Request):
    return templates.TemplateResponse("create.html",{"request":request,"title":"Create Car"})


@app.post("/cars",status_code=status.HTTP_201_CREATED) 
def add_cars(
    make:Optional[str] = Form(...),  #1
    model:Optional[str] = Form(...),
    year:Optional[int] = Form(...),
    price:Optional[float] = Form(...),
    engine:Optional[str] = Form(...),
    autonomous:Optional[bool] = Form(...), 
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
     
        
@app.get('/edit', response_class = HTMLResponse) #While the actual class is TemplateResponse, HTMLResponse is the top-level class to use.
def edit_car(request:Request, id:int = Query(...)):
    car = cars.get(id)
    if not car:
        return templates.TemplateResponse("search.html",{"request":request,"id":id,"title":"Edit car"},status_code=status.HTTP_404_NOT_FOUND )
    return templates.TemplateResponse("edit.html",{"request":request,"car":car,"id":id,"title":"Edit car"})
    
        

@app.post('/cars/{id}',response_class=HTMLResponse)
def update_car(request:Request, id:int,
    make:Optional[str] = Form(None),  #1
    model:Optional[str] = Form(None),
    year:Optional[str] = Form(None),
    price:Optional[float] = Form(None),
    engine:Optional[str] = Form(None),
    autonomous:Optional[bool] = Form(None), 
    sold: Optional[List[str]] = Form(None)):

    stored= cars.get(id)
    if not stored: 
        return templates.TemplateResponse('search.html',{"request":request, "id":id,"title":"Edit car"}, status_code=status.HTTP_404_NOT_FOUND)
    stored = Car(**dict(stored)) #2
    car = Car(make=make,model=model,year=year,price=price,engine=engine,autonomous=autonomous,sold=sold)
    new = car.dict(exclude_unset=True)
    new = stored.copy(update=new)
    cars[id] = jsonable_encoder(new)
    response ={}
    response[id] = cars[id]
    return RedirectResponse(url="/cars",status_code=302) #3

@app.get("/delete/{id}",response_class=RedirectResponse) #1
def delete_car(request:Request, id:int = Path(...)): #2
    if not cars.get(id):
        return templates.TemplateResponse('search.html',{"request":request, "id":id,"title":"Delete car"}, status_code=status.HTTP_404_NOT_FOUND)
    del cars[id]
    return RedirectResponse(url="/cars")
    

@app.post('/search', response_class=RedirectResponse)
def search_cars(id:str=Form(...)):
    return RedirectResponse("/cars/" + id, status_code=302) 


