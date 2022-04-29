from pydantic import BaseModel
from fastapi import Form
from typing import Optional

class User(BaseModel):
    name:str 
    age : Optional[int]
    address : Optional[str]
    
class UserIn(BaseModel):
    name : str 
    age : Optional[int] 
    address : Optional[str] 
    
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        age : Optional[int] =Form(None),
        address : Optional[str] =Form(None),
    ) -> "UserIn":
        return cls(name=name,age=age,address=address)
    
class UserDB(User):
    hashed_password :str
    