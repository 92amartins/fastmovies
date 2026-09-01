from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import torch
from lightning.pytorch import LightningModule, Trainer
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class TwoTowerRecommender:
    module: TwoTowerLightningModule
    movies: pd.DataFrame
    movie_index: dict[int, int]

    @classmethod
    def train(
        cls,
        ratings_path: str | Path,
        movies_path: str | Path,
        embedding_dim: int = 64,
        epochs: int = 10,
        batch_size: int = 1024,
    ) -> TwoTowerRecommender:
        ratings = pd.read_csv(ratings_path)
        movies = pd.read_csv(movies_path)
        return cls.train_from_frames(ratings, movies, embedding_dim, epochs, batch_size)

    @classmethod
    def train_from_frames(
        cls,
        ratings: pd.DataFrame,
        movies: pd.DataFrame,
        embedding_dim: int = 64,
        epochs: int = 10,
        batch_size: int = 1024,
    ) -> TwoTowerRecommender:
        required_ratings = {"userId", "movieId", "rating"}
        required_movies = {"movieId", "title", "genres"}
        if not required_ratings.issubset(ratings.columns):
            raise ValueError(f"ratings CSV must contain: {sorted(required_ratings)}")
        if not required_movies.issubset(movies.columns):
            raise ValueError(f"movies CSV must contain: {sorted(required_movies)}")
        if embedding_dim < 1 or epochs < 1 or batch_size < 1:
            raise ValueError("embedding_dim, epochs, and batch_size must be positive")

        user_indices, _ = pd.factorize(ratings["userId"])
        movie_indices, movie_ids = pd.factorize(ratings["movieId"])
        movie_ids = [int(movie_id) for movie_id in movie_ids]
        catalog = movies[movies["movieId"].isin(movie_ids)].copy()
        catalog["movieId"] = catalog["movieId"].astype(int)
        catalog = catalog.set_index("movieId").loc[movie_ids].reset_index()

        dataset = TensorDataset(
            torch.as_tensor(user_indices, dtype=torch.long),
            torch.as_tensor(movie_indices, dtype=torch.long),
            torch.as_tensor(ratings["rating"].to_numpy(), dtype=torch.float32),
        )
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        module = TwoTowerLightningModule(
            user_count=len(pd.unique(ratings["userId"])),
            movie_count=len(movie_ids),
            embedding_dim=embedding_dim,
        )
        trainer = Trainer(
            accelerator="cpu",
            devices=1,
            enable_checkpointing=False,
            enable_progress_bar=False,
            logger=False,
            max_epochs=epochs,
        )
        trainer.fit(module, train_dataloaders=loader)
        return cls(module, catalog, {movie_id: index for index, movie_id in enumerate(movie_ids)})

    def recommend(self, movie_id: int, limit: int = 10) -> list[dict[str, int | float | str]]:
        if movie_id not in self.movie_index:
            raise KeyError(movie_id)
        if limit < 1:
            return []

        with torch.no_grad():
            item_vectors = self.module.movie_tower.weight
            item_vectors = nn.functional.normalize(item_vectors, dim=1)
            scores = item_vectors @ item_vectors[self.movie_index[movie_id]]
        candidates = [
            (candidate_id, float(scores[index]))
            for candidate_id, index in self.movie_index.items()
            if candidate_id != movie_id
        ]
        candidates.sort(key=lambda item: item[1], reverse=True)
        movies_by_id = self.movies.set_index("movieId")
        return [
            {
                "movieId": candidate_id,
                "title": str(movies_by_id.loc[candidate_id, "title"]),
                "genres": str(movies_by_id.loc[candidate_id, "genres"]),
                "score": round(score, 4),
            }
            for candidate_id, score in candidates[:limit]
        ]

    def search_movies(self, query: str, limit: int = 10) -> list[dict[str, int | str]]:
        normalized_query = query.strip().casefold()
        if not normalized_query:
            return []
        matches = [
            {
                "movieId": int(row["movieId"]),
                "title": str(row["title"]),
                "genres": str(row["genres"]),
            }
            for row in self.movies.to_dict("records")
            if normalized_query in str(row["title"]).casefold()
        ]
        matches.sort(key=lambda movie: (str(movie["title"]).casefold(), movie["movieId"]))
        return matches[:limit]

    def save(self, path: str | Path) -> None:
        torch.save(
            {
                "state_dict": self.module.state_dict(),
                "user_count": self.module.user_tower.num_embeddings,
                "movie_count": self.module.movie_tower.num_embeddings,
                "embedding_dim": self.module.movie_tower.embedding_dim,
                "movies": self.movies,
                "movie_index": self.movie_index,
            },
            path,
        )

    @classmethod
    def load(cls, path: str | Path) -> TwoTowerRecommender:
        artifact: dict[str, Any] = torch.load(path, map_location="cpu", weights_only=False)
        module = TwoTowerLightningModule(
            user_count=artifact["user_count"],
            movie_count=artifact["movie_count"],
            embedding_dim=artifact["embedding_dim"],
        )
        module.load_state_dict(artifact["state_dict"])
        module.eval()
        return cls(module, artifact["movies"], artifact["movie_index"])


class TwoTowerLightningModule(LightningModule):
    def __init__(self, user_count: int, movie_count: int, embedding_dim: int) -> None:
        super().__init__()
        self.save_hyperparameters()
        self.user_tower = nn.Embedding(user_count, embedding_dim)
        self.movie_tower = nn.Embedding(movie_count, embedding_dim)
        self.loss = nn.MSELoss()

    def forward(self, user_indices: Tensor, movie_indices: Tensor) -> Tensor:
        user_vectors = self.user_tower(user_indices)
        movie_vectors = self.movie_tower(movie_indices)
        return (user_vectors * movie_vectors).sum(dim=1)

    def training_step(self, batch: tuple[Tensor, Tensor, Tensor], _: int) -> Tensor:
        user_indices, movie_indices, ratings = batch
        predictions = self(user_indices, movie_indices)
        loss = self.loss(predictions, ratings)
        self.log("train_loss", loss, prog_bar=False)
        return loss

    def configure_optimizers(self) -> torch.optim.Optimizer:
        return torch.optim.Adam(self.parameters(), lr=0.01)
