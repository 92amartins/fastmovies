from __future__ import annotations

import argparse
from pathlib import Path

from app.recommender import MovieRecommender


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a MovieLens item-based recommender")
    parser.add_argument("--ratings", default="ml-latest-small/ratings.csv")
    parser.add_argument("--movies", default="ml-latest-small/movies.csv")
    parser.add_argument("--output", default="model.joblib")
    args = parser.parse_args()

    model = MovieRecommender.train(args.ratings, args.movies)
    model.save(args.output)
    print(f"Saved model with {len(model.movies)} movies to {Path(args.output)}")


if __name__ == "__main__":
    main()
