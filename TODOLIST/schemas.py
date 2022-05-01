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