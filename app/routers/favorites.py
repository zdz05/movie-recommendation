from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import FavoriteCreate, FavoriteResponse
from app.services import favorite_service

router = APIRouter(prefix="/api/v1/favorite", tags=["favorites"])


@router.get("", response_model=list[FavoriteResponse])
def get_favorites(db: Session = Depends(get_db)):
    return favorite_service.get_favorites(db)


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(favorite: FavoriteCreate, db: Session = Depends(get_db)):
    return favorite_service.add_favorite(db, favorite)


@router.delete("/{tmdb_id}", response_model=str)
def delete_favorite(tmdb_id: int, db: Session = Depends(get_db)):
    favorite_service.delete_favorite(db, tmdb_id)
    return "Favorite deleted successfully"
