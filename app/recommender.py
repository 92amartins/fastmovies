from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MovieRecommender:
    movies: pd.DataFrame
    similarity: Any
    movie_index: dict[int, int]

    @classmethod
    def train(cls, ratings_path: str | Path, movies_path: str | Path) -> MovieRecommender:
        ratings = pd.read_csv(ratings_path)
        movies = pd.read_csv(movies_path)
        return cls.train_from_frames(ratings, movies)

    @classmethod
    def train_from_frames(
        cls, ratings: pd.DataFrame, movies: pd.DataFrame
    ) -> MovieRecommender:
        required_ratings = {"userId", "movieId", "rating"}
        required_movies = {"movieId", "title", "genres"}
        if not required_ratings.issubset(ratings.columns):
            raise ValueError(f"ratings CSV must contain: {sorted(required_ratings)}")
        if not required_movies.issubset(movies.columns):
            raise ValueError(f"movies CSV must contain: {sorted(required_movies)}")

        user_movie = ratings.pivot_table(
            index="movieId", columns="userId", values="rating", fill_value=0
        )
        movie_ids = user_movie.index.astype(int).tolist()
        similarity = cosine_similarity(user_movie)
        catalog = movies[movies["movieId"].isin(movie_ids)].copy()
        catalog["movieId"] = catalog["movieId"].astype(int)
        catalog = catalog.set_index("movieId").loc[movie_ids].reset_index()
        return cls(catalog, similarity, {movie_id: i for i, movie_id in enumerate(movie_ids)})

    def recommend(self, movie_id: int, limit: int = 10) -> list[dict[str, Any]]:
        if movie_id not in self.movie_index:
            raise KeyError(movie_id)
        row = self.movie_index[movie_id]
        scores = self.similarity[row]
        candidates = [
            (candidate_id, float(scores[index]))
            for candidate_id, index in self.movie_index.items()
            if candidate_id != movie_id
        ]
        candidates.sort(key=lambda item: item[1], reverse=True)
        selected = candidates[:limit]
        movies_by_id = self.movies.set_index("movieId")
        return [
            {
                "movieId": candidate_id,
                "title": str(movies_by_id.loc[candidate_id, "title"]),
                "genres": str(movies_by_id.loc[candidate_id, "genres"]),
                "score": round(score, 4),
            }
            for candidate_id, score in selected
        ]

    def save(self, path: str | Path) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str | Path) -> MovieRecommender:
        model = joblib.load(path)
        if not isinstance(model, cls):
            raise TypeError("The model file does not contain a MovieRecommender")
        return model
