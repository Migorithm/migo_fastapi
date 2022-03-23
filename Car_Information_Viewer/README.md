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