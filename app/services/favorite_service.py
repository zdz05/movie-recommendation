from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.schemas.movie import FavoriteCreate


def get_favorites(db: Session) -> list[Favorite]:
    return db.query(Favorite).all()


def add_favorite(db: Session, favorite: FavoriteCreate) -> Favorite:
    db_favorite = Favorite(**favorite.model_dump())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def delete_favorite(db: Session, tmdb_id: int) -> None:
    db.query(Favorite).filter(Favorite.tmdb_id == tmdb_id).delete()
    db.commit()
