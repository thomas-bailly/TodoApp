from fastapi import FastAPI
from todo_api.database import Base, engine
from todo_api import models

from todo_api.config import settings

# FastAPI application initialization
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Root"])
async def root():
    return {'message': 'Welcome to the Todo App API. Visit /docs for documentation.'}