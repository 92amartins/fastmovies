from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MovieRecommender:
    movies: pd.DataFrame
    similarity: Any
    movie_index: dict[int, int]
    neighbor_indices: Any | None = None
    neighbor_scores: Any | None = None

    @classmethod
    def train(cls, ratings_path: str | Path, movies_path: str | Path) -> MovieRecommender:
        ratings = pd.read_csv(ratings_path)
        movies = pd.read_csv(movies_path)
        return cls.train_from_frames(ratings, movies)

    @classmethod
    def train_from_frames(
        cls, ratings: pd.DataFrame, movies: pd.DataFrame, neighbors: int = 100
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
        neighbor_count = min(neighbors + 1, len(movie_ids))
        neighbor_indices = similarity.argsort(axis=1)[:, -neighbor_count:][:, ::-1]
        neighbor_scores = similarity[
            np.arange(len(movie_ids))[:, None], neighbor_indices
        ].astype("float32")
        catalog = movies[movies["movieId"].isin(movie_ids)].copy()
        catalog["movieId"] = catalog["movieId"].astype(int)
        catalog = catalog.set_index("movieId").loc[movie_ids].reset_index()
        return cls(
            catalog,
            similarity=None,
            movie_index={movie_id: i for i, movie_id in enumerate(movie_ids)},
            neighbor_indices=neighbor_indices.astype("int32"),
            neighbor_scores=neighbor_scores,
        )

    def recommend(self, movie_id: int, limit: int = 10) -> list[dict[str, int | float | str]]:
        if movie_id not in self.movie_index:
            raise KeyError(movie_id)
        row = self.movie_index[movie_id]
        if self.neighbor_indices is not None and self.neighbor_scores is not None:
            movie_ids_by_index = {index: movie_id for movie_id, index in self.movie_index.items()}
            candidates = [
                (movie_ids_by_index[index], float(score))
                for index, score in zip(self.neighbor_indices[row], self.neighbor_scores[row])
                if movie_ids_by_index[index] != movie_id
            ]
        else:
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

    def search_movies(self, query: str, limit: int = 10) -> list[dict[str, int | str]]:
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return []

        matches = [
            {
                "movieId": int(movie_id),
                "title": str(row["title"]),
                "genres": str(row["genres"]),
            }
            for row in self.movies.to_dict("records")
            for movie_id in [row["movieId"]]
            if movie_id in self.movie_index
            and normalized_query in str(row["title"]).casefold()
        ]
        matches.sort(key=lambda movie: (str(movie["title"]).casefold(), movie["movieId"]))
        return matches[:limit]

    def save(self, path: str | Path) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str | Path) -> MovieRecommender:
        model = joblib.load(path)
        if not isinstance(model, cls):
            raise TypeError("The model file does not contain a MovieRecommender")
        return model
