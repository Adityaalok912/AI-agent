import os
from fastapi import FastAPI

# this name of variable 'app' is same that is used in compose file line 8   (command: uvicorn main:app --host 0.0.0.0 --port 8000)
app = FastAPI() 

API_KEY = os.environ.get("API_KEY")

@app.get("/")
def read_index():
    return {"Hello": "World!!"}