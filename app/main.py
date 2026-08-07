from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers.favorites import router as favorites_router
from app.routers.movies import router as movies_router
from app.routers.recommendations import router as recommendations_router
from app.services import recommendation_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    recommendation_service.load_model()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Movie search, favorites, and recommendations",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(movies_router)
app.include_router(favorites_router)
app.include_router(recommendations_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
