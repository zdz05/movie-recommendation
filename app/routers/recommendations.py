from fastapi import APIRouter

from app.schemas.movie import MovieResponse

router = APIRouter(prefix="/api/v1/recommendation", tags=["recommendations"])


@router.get("", response_model=list[MovieResponse])
def get_recommendations():
    return []
