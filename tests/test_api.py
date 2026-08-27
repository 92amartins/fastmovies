from __future__ import annotations

import pandas as pd
from fastapi.testclient import TestClient

from app import main
from app.recommender import MovieRecommender


def test_root_serves_frontend() -> None:
    response = TestClient(main.app).get("/")
    assert response.status_code == 200
    assert "Framefinder" in response.text


def test_frontend_assets_are_served() -> None:
    response = TestClient(main.app).get("/static/app.js")
    assert response.status_code == 200
    assert "loadRecommendations" in response.text


def test_health_without_model() -> None:
    main.model = None
    response = TestClient(main.app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": False}


def test_movies_search_returns_matching_catalog_entries() -> None:
    main.model = MovieRecommender(
        pd.DataFrame(
            {
                "movieId": [1, 2, 3],
                "title": ["The Matrix", "Toy Story", "Matrix Reloaded"],
                "genres": ["Action", "Animation", "Action"],
            }
        ),
        [[1.0]],
        {1: 0, 2: 1, 3: 2},
    )
    response = TestClient(main.app).get("/movies?query=matrix")
    assert response.status_code == 200
    assert response.json() == [
        {"movieId": 3, "title": "Matrix Reloaded", "genres": "Action"},
        {"movieId": 1, "title": "The Matrix", "genres": "Action"},
    ]


def test_movies_requires_a_query() -> None:
    main.model = MovieRecommender(
        pd.DataFrame({"movieId": [1], "title": ["Alpha"], "genres": ["Action"]}),
        [[1.0]],
        {1: 0},
    )
    response = TestClient(main.app).get("/movies")
    assert response.status_code == 422


def test_movies_without_model_returns_service_unavailable() -> None:
    main.model = None
    response = TestClient(main.app).get("/movies?query=matrix")
    assert response.status_code == 503


def test_recommendations_returns_similar_movies() -> None:
    movies = pd.DataFrame(
        {
            "movieId": [1, 2, 3],
            "title": ["Alpha", "Beta", "Gamma"],
            "genres": ["Action", "Action", "Comedy"],
        }
    )
    ratings = pd.DataFrame(
        {
            "userId": [1, 1, 2, 2, 3, 3],
            "movieId": [1, 2, 1, 2, 1, 3],
            "rating": [5, 5, 4, 4, 5, 1],
        }
    )
    main.model = MovieRecommender.train_from_frames(ratings, movies)
    response = TestClient(main.app).get("/recommendations?movie_id=1&limit=1")
    assert response.status_code == 200
    assert response.json()["recommendations"][0]["movieId"] == 2


def test_unknown_movie_returns_not_found() -> None:
    main.model = MovieRecommender(
        pd.DataFrame({"movieId": [1], "title": ["Alpha"], "genres": ["Action"]}),
        [[1.0]],
        {1: 0},
    )
    response = TestClient(main.app).get("/recommendations?movie_id=99")
    assert response.status_code == 404
