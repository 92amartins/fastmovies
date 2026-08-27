from __future__ import annotations

import argparse
from pathlib import Path

from app.recommender import MovieRecommender


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a MovieLens item-based recommender")
    parser.add_argument("--ratings", default="data/ml-latest-small/ratings.csv")
    parser.add_argument("--movies", default="data/ml-latest-small/movies.csv")
    parser.add_argument("--output", default="model.joblib")
    parser.add_argument("--model", choices=("item", "two_tower"), default="item")
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=1024)
    args = parser.parse_args()

    if args.model == "two_tower":
        from app.two_tower import TwoTowerRecommender

        model = TwoTowerRecommender.train(
            args.ratings,
            args.movies,
            embedding_dim=args.embedding_dim,
            epochs=args.epochs,
            batch_size=args.batch_size,
        )
    else:
        model = MovieRecommender.train(args.ratings, args.movies)
    model.save(args.output)
    print(f"Saved model with {len(model.movies)} movies to {Path(args.output)}")


if __name__ == "__main__":
    main()
