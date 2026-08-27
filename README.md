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

Para treinar o modelo two-tower com PyTorch Lightning:

```powershell
uv run python -m scripts.train --model two_tower --output model.pt
```

Ao iniciar a API com esse artefato, defina `MODEL_PATH=model.pt` e
`MODEL_TYPE=two_tower`.

Inicie a API:

```powershell
uv run uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000/` no navegador para usar a interface de recomendações.
Os filmes podem ser buscados por título; a documentação interativa continua disponível em
`http://127.0.0.1:8000/docs`.

Endpoints:

- `GET /health`
- `GET /movies?query=matrix&limit=10`
- `GET /recommendations?movie_id=1&limit=10`
- `GET /docs`

`/movies` retorna filmes do catálogo do modelo com `movieId`, `title` e `genres`.
O parâmetro `limit` aceita valores de 1 a 50. A interface usa esse resultado para
selecionar um filme antes de consultar `/recommendations`.

O caminho do modelo pode ser alterado com a variável de ambiente `MODEL_PATH`.
O arquivo `model.joblib` precisa estar presente no diretório enviado para o deploy.
Como ele é um artefato local grande, confirme no resumo do `fastapi deploy` que ele
foi incluído; a regra `!model.joblib` no `.gitignore` permite que o FastAPI Cloud o
encontre sem exigir que o arquivo seja commitado.

## Testes

```powershell
uv run pytest
```
