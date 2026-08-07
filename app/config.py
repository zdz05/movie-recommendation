from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Movie Recommendation API"
    database_url: str = "postgresql://postgres:postgres@db:5432/movies"
    tmdb_api_key: str = ""
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    movielens_dir: str = "../ml-25m"


settings = Settings()
