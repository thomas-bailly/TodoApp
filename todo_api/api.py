from fastapi import FastAPI
from todo_api.database import Base, engine
from todo_api import models


# FastAPI application initialization
app = FastAPI(
    title="TodoApp RESTful API",
    description="A RESTful API for managing user tasks.",
    version="0.1.0"
)

Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Root"])
async def root():
    return {'message': 'Welcome to the Todo App API. Visit /docs for documentation.'}