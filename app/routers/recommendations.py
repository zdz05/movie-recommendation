from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import RecommendationResponse
from app.services import favorite_service, recommendation_service

router = APIRouter(prefix="/api/v1/recommendation", tags=["recommendations"])


@router.get("", response_model=list[RecommendationResponse])
def get_recommendations(db: Session = Depends(get_db)):
    favorites = favorite_service.get_favorites(db)
    return recommendation_service.get_recommendations(favorites)
