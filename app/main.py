from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.recommender import MovieRecommender

MODEL_PATH = Path(os.getenv("MODEL_PATH", "model.joblib"))
model: MovieRecommender | None = None


class Recommendation(BaseModel):
    movieId: int
    title: str
    genres: str
    score: float


class RecommendationResponse(BaseModel):
    movieId: int
    recommendations: list[Recommendation]


@asynccontextmanager
async def lifespan(_: FastAPI):
    global model
    if MODEL_PATH.exists():
        model = MovieRecommender.load(MODEL_PATH)
    yield


app = FastAPI(title="MovieLens Recommender API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/recommendations", response_model=RecommendationResponse)
def recommendations(
    movie_id: int = Query(..., gt=0),
    limit: int = Query(10, ge=1, le=100),
) -> RecommendationResponse:
    if model is None:
        raise HTTPException(status_code=503, detail="Recommendation model is not loaded")
    try:
        results = model.recommend(movie_id, limit)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Movie {movie_id} was not found") from None
    return RecommendationResponse(movieId=movie_id, recommendations=results)
