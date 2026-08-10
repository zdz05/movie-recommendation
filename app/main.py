from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.movies import router as movies_router
from app.routers.recommendations import router as recommendations_router
from app.services import recommendation_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    recommendation_service.load_model()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Movie search and ML recommendations",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router)
app.include_router(recommendations_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
