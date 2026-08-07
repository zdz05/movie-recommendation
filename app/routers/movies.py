from fastapi import APIRouter, Query

from app.schemas.movie import MovieResponse
from app.services import tmdb_service

router = APIRouter(prefix="/api/v1/movie", tags=["movies"])


@router.get("", response_model=list[MovieResponse])
def get_movies(
    query: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
):
    if query:
        return tmdb_service.search_movies(query, page)
    return tmdb_service.get_popular_movies(page)
