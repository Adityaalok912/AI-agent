import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.db import init_db

from api.chat.routing import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app starts
    init_db()
    yield
    # after app startup

# this name of variable 'app' is same that is used in compose file line 8   (command: uvicorn main:app --host 0.0.0.0 --port 8000)
app = FastAPI(lifespan=lifespan) 
app.include_router(chat_router, prefix="/api/chats")

API_KEY = os.environ.get("API_KEY")

@app.get("/")
def read_index():
    return {"Hello": "World!!"}