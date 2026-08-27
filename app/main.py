from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.recommender import Recommender, load_recommender

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "model.joblib"
FRONTEND_PATH = Path(__file__).resolve().parents[1] / "frontend"
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH)))
MODEL_TYPE = os.getenv("MODEL_TYPE", "item")
model: Recommender | None = None


class Recommendation(BaseModel):
    movieId: int
    title: str
    genres: str
    score: float


class RecommendationResponse(BaseModel):
    movieId: int
    recommendations: list[Recommendation]


class Movie(BaseModel):
    movieId: int
    title: str
    genres: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    global model
    if MODEL_PATH.exists():
        model = load_recommender(MODEL_PATH, MODEL_TYPE)
    yield


app = FastAPI(title="MovieLens Recommender API", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(FRONTEND_PATH / "index.html")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/movies", response_model=list[Movie])
def movies(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
) -> list[Movie]:
    if model is None:
        raise HTTPException(status_code=503, detail="Recommendation model is not loaded")
    return [Movie(**movie) for movie in model.search_movies(query, limit)]


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
