from fastapi import APIRouter

from app.schemas.movie import FavoriteCreate, RecommendationResponse
from app.services import recommendation_service

router = APIRouter(prefix="/api/v1/recommendation", tags=["recommendations"])


@router.post("", response_model=list[RecommendationResponse])
def get_recommendations(favorites: list[FavoriteCreate]):
    return recommendation_service.get_recommendations(favorites)
