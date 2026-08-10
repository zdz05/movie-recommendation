import re
import zipfile
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.schemas.movie import RecommendationResponse

ML25M_URL = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
REQUIRED_FILES = ("movies.csv", "ratings.csv", "links.csv")

movies: pd.DataFrame | None = None
ratings: pd.DataFrame | None = None
links: pd.DataFrame | None = None
vectorizer: TfidfVectorizer | None = None
tfidf = None


def clean_title(title: str) -> str:
    return re.sub("[^a-zA-Z0-9 ]", "", title)


def ensure_movielens_data(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)

    if all((data_dir / name).exists() for name in REQUIRED_FILES):
        return

    zip_path = data_dir / "ml-25m.zip"
    if not zip_path.exists():
        with httpx.stream("GET", ML25M_URL, follow_redirects=True, timeout=300.0) as response:
            response.raise_for_status()
            with zip_path.open("wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in REQUIRED_FILES:
            target = data_dir / name
            if target.exists():
                continue
            with zf.open(f"ml-25m/{name}") as src, target.open("wb") as dst:
                dst.write(src.read())


def load_model() -> None:
    global movies, ratings, links, vectorizer, tfidf

    data_dir = Path(settings.movielens_dir)
    ensure_movielens_data(data_dir)

    movies = pd.read_csv(data_dir / "movies.csv")
    ratings = pd.read_csv(data_dir / "ratings.csv")
    links = pd.read_csv(data_dir / "links.csv")

    movies = movies.copy()
    movies["clean_title"] = movies["title"].apply(clean_title)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf = vectorizer.fit_transform(movies["clean_title"])


def search(title: str) -> pd.DataFrame:
    cleaned = clean_title(title)
    query_vec = vectorizer.transform([cleaned])
    similarity = cosine_similarity(query_vec, tfidf).flatten()
    indices = np.argpartition(similarity, -5)[-5:]
    return movies.iloc[indices].iloc[::-1]


def find_similar_movies(movie_id: int) -> pd.DataFrame:
    similar_users = ratings[
        (ratings["movieId"] == movie_id) & (ratings["rating"] > 4)
    ]["userId"].unique()
    similar_user_recs = ratings[
        (ratings["userId"].isin(similar_users)) & (ratings["rating"] > 4)
    ]["movieId"]
    similar_user_recs = similar_user_recs.value_counts() / len(similar_users)
    similar_user_recs = similar_user_recs[similar_user_recs > 0.10]

    all_users = ratings[
        (ratings["movieId"].isin(similar_user_recs.index)) & (ratings["rating"] > 4)
    ]
    all_user_recs = all_users["movieId"].value_counts() / len(all_users["userId"].unique())

    rec_percentages = pd.concat([similar_user_recs, all_user_recs], axis=1)
    rec_percentages.columns = ["similar", "all"]
    rec_percentages["score"] = rec_percentages["similar"] / rec_percentages["all"]
    rec_percentages = rec_percentages.sort_values("score", ascending=False)

    return rec_percentages.head(10).merge(
        movies, left_index=True, right_on="movieId"
    )[["score", "movieId", "title", "genres"]]


def _movie_id_from_tmdb(tmdb_id: int) -> int | None:
    match = links[links["tmdbId"] == tmdb_id]
    if match.empty:
        return None
    return int(match.iloc[0]["movieId"])


def _movie_id_for_favorite(favorite) -> int | None:
    movie_id = _movie_id_from_tmdb(favorite.tmdb_id)
    if movie_id is not None:
        return movie_id

    results = search(favorite.title)
    if results.empty:
        return None
    return int(results.iloc[0]["movieId"])


def get_recommendations(favorites) -> list[RecommendationResponse]:
    if not favorites:
        return []

    favorite_movie_ids: set[int] = set()
    scores: dict[int, float] = {}

    for favorite in favorites:
        movie_id = _movie_id_for_favorite(favorite)
        if movie_id is None:
            continue

        favorite_movie_ids.add(movie_id)
        recs = find_similar_movies(movie_id)

        for _, row in recs.iterrows():
            rec_id = int(row["movieId"])
            if rec_id in favorite_movie_ids:
                continue

            score = float(row["score"])
            if rec_id in scores:
                scores[rec_id] = max(scores[rec_id], score)
            else:
                scores[rec_id] = score

    top_ids = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:10]
    tmdb_lookup = links.set_index("movieId")["tmdbId"].to_dict()

    recommendations = []
    for movie_id, score in top_ids:
        movie = movies[movies["movieId"] == movie_id].iloc[0]
        tmdb_id = tmdb_lookup.get(movie_id)
        recommendations.append(
            RecommendationResponse(
                movie_id=movie_id,
                tmdb_id=int(tmdb_id) if pd.notna(tmdb_id) else None,
                title=movie["title"],
                genres=movie["genres"],
                score=score,
            )
        )

    return recommendations
