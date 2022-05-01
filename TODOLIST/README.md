# About this toy project

In this project, I'll be focusing mainly on interacting with Database using SQLAlchemy

```sh
pip install sqlalchemy
pip install alembic #For database migration
```

## Setting up Database

**db.py**
```python
from sqlalchemy import create_engine #1
from sqlalchemy.ext.declarative import declarative_base #2
from sqlalchemy.orm import session,sessionmaker #3
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

#Constant variable that references to the database. 
SQLALCHEMY_DATABASE_URI=f"sqlite://{BASEDIR}/todo_app.db"  

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread":False} #4
)

SessionLocal= sessionmaker( #5
        autocommit=False,
        autoflush=False,
        bind=engine #6
    )

Base = declarative_base()

#7
class DBContext:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self): #Equivalent to opening the file and getting all of the file contents and storing it under a variable
        return self.db

    def __exit__(self,execution_type,execution_value,traceback): #8 even though we don't use them, we need to pass in extra parameters
        self.db.close()


```
1. This will initialize engine that works with database. 
2. Class initializer that will creata the base. It stores columns, models and tabels and rows. 
3. session and session makar to work with database session. 
4. By default, SQLite doesn't allow multiple requests to work. But FastAPI is set up in a way that's basically forced to do that with dependencies. For now, let's disable 'check_same_thread' to make sure each request is individual and a unique request.

5. SessionLocal is used to actually initialize database session. 
6. It is to bind the session to engine.
7. We need to create something for database context that creates database session and closes the session. This is important because we are going to use dependencies. With dependencies, we don't have much control over what runs first and what runs last. So we need to make sure that the database will open and close and give us the actual session whenever we need it. 



## Creating Pydantic Models
We need two separate Pydantic Models 
- One for reading
- one for creating(or writing)
<br>

**schemas.py:**
```python
from pydantic import BaseModel
from typing import List, Optional

class TaskBase(BaseModel):
    text :str

class Task(TaskBase):
    id: str
    user_id : str

    class Config:
        orm_mode =True #1

class TaskCreate(TaskBase):
    pass

class UserBase(BaseModel):
    #2
    username: str
    email : str
    hashed_password: str

class User(UserBase): #read 
    id : str
    tasks : List[Task] = []
    
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    pass

```
1. We are going to read data from DB, so data is not dictionaries or JSON anymore. By doing this, it's going to allow the pydantic model to actually take this data to create the classes instead of restriting it to dictionaries. (By default, it doesn't allow reading other types of object representation such as ones in SQL)

2. As we'll be working with database migration, let's pretend to omit name field. Somewhere later we will add the name field. 