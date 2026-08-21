# MovieLens Recommender API

API FastAPI para recomendações de filmes usando filtragem colaborativa item-based e similaridade de cosseno.

## Setup

Instale o [uv](https://docs.astral.sh/uv/getting-started/installation/) e execute os comandos a partir da raiz do projeto:

```powershell
uv sync
```

Baixe o dataset `ml-latest-small` do MovieLens e extraia a pasta na raiz do projeto. Depois treine o modelo:

```powershell
uv run python scripts/train.py
```

Inicie a API:

```powershell
uv run uvicorn app.main:app --reload
```

Endpoints:

- `GET /health`
- `GET /recommendations?movie_id=1&limit=10`
- `GET /docs`

O caminho do modelo pode ser alterado com a variável de ambiente `MODEL_PATH`.

## Testes

```powershell
uv run pytest
```
