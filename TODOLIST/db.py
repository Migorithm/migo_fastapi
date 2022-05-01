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