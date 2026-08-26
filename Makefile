.PHONY: help dependencies run test train deploy

help:
	@echo "Available commands:"
	@echo "  make dependencies  Install/sync dependencies"
	@echo "  make run           Start the API"
	@echo "  make test          Run tests"
	@echo "  make train         Train the recommender model"
	@echo "  make deploy        Deploy to FastAPI Cloud"

dependencies:
	uv sync

run:
	uv run fastapi run --host 127.0.0.1

dev:
	uv run fastapi dev

test:
	uv run pytest

train:
	uv run python -m scripts.train

deploy:
	uv run fastapi deploy