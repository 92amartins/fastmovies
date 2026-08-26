.PHONY: help dependencies run test train

help:
	@echo "Available commands:"
	@echo "  make dependencies  Install/sync dependencies"
	@echo "  make run           Start the API"
	@echo "  make test          Run tests"
	@echo "  make train         Train the recommender model"

dependencies:
	uv sync

run:
	uv run fastapi run

dev:
	uv run fastapi dev

test:
	uv run pytest

train:
	uv run python -m scripts.train