from pydantic import BaseModel


class MovieResponse(BaseModel):
    tmdb_id: int
    title: str
    overview: str | None = None
    poster_path: str | None = None
    release_date: str | None = None
    vote_average: float | None = None


class FavoriteCreate(BaseModel):
    tmdb_id: int
    title: str
    overview: str | None = None
    poster_path: str | None = None
    release_date: str | None = None


class RecommendationResponse(BaseModel):
    movie_id: int
    tmdb_id: int | None = None
    title: str
    genres: str | None = None
    score: float
