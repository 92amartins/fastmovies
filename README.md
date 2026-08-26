# MovieLens Recommender API

API FastAPI para recomendações de filmes usando filtragem colaborativa item-based e similaridade de cosseno.

## Setup

Instale o [uv](https://docs.astral.sh/uv/getting-started/installation/) e execute os comandos a partir da raiz do projeto:

```powershell
uv sync
```

Baixe o dataset `ml-latest-small` do MovieLens e extraia a pasta na raiz do projeto. Depois treine o modelo:

```powershell
uv run python -m scripts.train
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
O arquivo `model.joblib` precisa estar presente no diretório enviado para o deploy.
Como ele é um artefato local grande, confirme no resumo do `fastapi deploy` que ele
foi incluído; a regra `!model.joblib` no `.gitignore` permite que o FastAPI Cloud o
encontre sem exigir que o arquivo seja commitado.

## Testes

```powershell
uv run pytest
```
