import httpx

from app.config import settings
from app.schemas.movie import MovieResponse


def _map_movie(movie: dict) -> MovieResponse:
    return MovieResponse(
        tmdb_id=movie["id"],
        title=movie["title"],
        overview=movie.get("overview"),
        poster_path=movie.get("poster_path"),
        release_date=movie.get("release_date"),
        vote_average=movie.get("vote_average"),
    )


def get_popular_movies(page: int = 1) -> list[MovieResponse]:
    url = f"{settings.tmdb_base_url}/movie/popular"
    params = {"api_key": settings.tmdb_api_key, "page": page}

    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()
    return [_map_movie(movie) for movie in response.json()["results"]]


def search_movies(query: str, page: int = 1) -> list[MovieResponse]:
    url = f"{settings.tmdb_base_url}/search/movie"
    params = {"api_key": settings.tmdb_api_key, "query": query, "page": page}

    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()
    return [_map_movie(movie) for movie in response.json()["results"]]
