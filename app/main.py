from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="FastAPI backend",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to the API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
