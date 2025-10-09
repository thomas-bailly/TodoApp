from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from todo_api.database import Base, engine
from todo_api import models
from todo_api.routers.auth import router as auth_router
from todo_api.routers.user import router as user_router
from todo_api.config import settings

# FastAPI application initialization
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version
)

Base.metadata.create_all(bind=engine)

@app.exception_handler(IntegrityError)
async def integrety_error_handler(resquest: Request, exc: IntegrityError) -> JSONResponse:
    detail = "Database integrity error."
    
    if "UNIQUE constraint failed" in str(exc.orig):
        if "username" in str(exc.orig):
            detail = "Username already exists."
        elif "email" in str(exc.orig):
            detail = "Email already exists."
        else:
            detail = "Unique constraint violation."
            
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": detail}
    )

@app.get("/", tags=["Root"])
async def root():
    return {'message': 'Welcome to the Todo App API. Visit /docs for documentation.'}

app.include_router(auth_router)
app.include_router(user_router)