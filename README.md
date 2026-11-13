# Cake API

API REST para gestão de uma confeitaria/loja de bolos: usuários, categorias, produtos, orçamentos (budgets) e membros da equipe. Construída com **FastAPI**, **SQLAlchemy 2.0**, **Pydantic v2** e **PostgreSQL**, com autenticação JWT.

## Arquitetura

Fluxo em camadas, com injeção de dependência do FastAPI (`Depends`) em todos os níveis:

```text
routes → controllers → services → repositories → models (SQLAlchemy)
                ↑           ↑            ↑
              DTOs      regras de    acesso a
           (Pydantic)   negócio      dados
```

- **`api/routes/`** — declaração de endpoints (path, `response_model`, status code). Finas: apenas delegam ao controller.
- **`api/controllers/`** — orquestração HTTP: validações de existência (404), conflitos (409), permissões (403). Injetados via `Depends()`.
- **`api/dtos/`** — DTOs Pydantic (`*Create`, `*Update`, `*Read`) usados como entrada/saída da API.
- **`services/`** — regras de negócio (ex.: hash de senha, autenticação). Injetados via `Depends()`.
- **`repositories/`** — única camada que fala com o SQLAlchemy (`Session`, queries). `BaseRepository[ModelT]` genérico + repositórios por entidade.
- **`models/`** — modelos SQLAlchemy 2.0 (`Mapped`/`mapped_column`).
- **`core/`** — configuração (`pydantic-settings`) e segurança (bcrypt + JWT).
- **`database/`** — `Base` declarativa, engine, `get_db` e `init_db`.

### Modelo de dados

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : "é usada em"
    CATEGORY {
        int id PK
        string label UK
        string icon
    }
    PRODUCT {
        int id PK
        string name
        text description
        numeric price
        numeric rating
        string image_url
        int category_id FK
        int stock
    }
    USER {
        int id PK
        string name
        string password
        string email_address UK
        bool is_active
    }
    BUDGET {
        int id PK
        string code UK
        string customer
        text description
        date date
        numeric amount
        enum status
        string initials
    }
    TEAM_MEMBER {
        int id PK
        string name
        string role
        string email_address UK
        string phone
        enum status
        string initials
        string color
    }
```

`Category 1—N Product` com `ondelete="CASCADE"` e `cascade="all, delete-orphan"`.

## Requisitos

- Docker + Docker Compose (recomendado), **ou**
- Python 3.12+ e um PostgreSQL acessível

## Subindo com Docker Compose (recomendado)

```bash
cp .env.example .env      # ajuste se necessário
docker compose up -d --build
```

Isso sobe dois serviços:

| Serviço | Imagem | Porta no host | Descrição |
|---------|--------|---------------|-----------|
| `db`    | `postgres:16-alpine` | `5433` → `5432` | PostgreSQL com volume `postgres_data` e healthcheck `pg_isready` |
| `api`   | build local (`Dockerfile`) | `8000` → `8000` | FastAPI/Uvicorn; sobe após o `db` ficar saudável |

A API cria as tabelas automaticamente no startup (`init_db()` com retries).

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

Comandos úteis:

```bash
docker compose logs -f api     # logs da API
docker compose ps              # status dos serviços
docker compose down            # parar (mantém os dados)
docker compose down -v         # parar e apagar o volume do Postgres
```

> A porta `5433` no host evita conflito com um PostgreSQL local na `5432`. Dentro da rede do compose, a API acessa o banco em `db:5432`.

## Rodando localmente (sem Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite DATABASE_URL para apontar para o seu Postgres, ex.:
# DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/cakeapi

uvicorn main:app --reload
```

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `POSTGRES_USER` | `cakeapi` | Usuário do Postgres (compose) |
| `POSTGRES_PASSWORD` | `cakeapi` | Senha do Postgres (compose) |
| `POSTGRES_DB` | `cakeapi` | Nome do banco (compose) |
| `POSTGRES_PORT` | `5433` | Porta exposta no host (compose) |
| `API_PORT` | `8000` | Porta exposta pela API no host (compose) |
| `DATABASE_URL` | `postgresql+psycopg://cakeapi:cakeapi@localhost:5433/cakeapi` | URL usada pela API fora do compose |
| `SECRET_KEY` | — | Chave HMAC para assinar os JWTs (**troque em produção**) |
| `ALGORITHM` | `HS256` | Algoritmo do JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Validade do token |

> Dentro do compose, `DATABASE_URL` é montado automaticamente a partir de `POSTGRES_*` apontando para `db:5432`.

## Endpoints

Base URL: `http://127.0.0.1:8000`

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| POST | `/auth/login` | Login (JSON: `email_address`, `password`) → `{access_token, token_type}` |
| POST | `/auth/token` | Login OAuth2 (form) — usado pelo Swagger |
| GET/POST | `/users` | Listar / criar usuários |
| GET/PATCH/DELETE | `/users/{id}` | Detalhar / atualizar / remover |
| GET | `/users/me` | Usuário autenticado (Bearer) |
| POST | `/users/{id}/change-password` | Trocar senha (Bearer, apenas o próprio usuário) |
| POST | `/users/{id}/activate` · `/deactivate` | Ativar / desativar |
| GET/POST | `/categories` | Listar / criar categorias |
| GET/PATCH/DELETE | `/categories/{id}` | Detalhar / atualizar / remover |
| GET | `/categories/{id}/products` | Categoria com seus produtos |
| GET/POST | `/products` | Listar (`?category_id=`) / criar |
| GET/PATCH/DELETE | `/products/{id}` | Detalhar / atualizar / remover |
| GET/POST | `/budgets` | Listar (`?status_filter=pending\|approved\|rejected\|paid`) / criar |
| GET/PATCH/DELETE | `/budgets/{id}` | Detalhar / atualizar / remover |
| GET/POST | `/team-members` | Listar (`?status_filter=active\|inactive\|on_leave`) / criar |
| GET/PATCH/DELETE | `/team-members/{id}` | Detalhar / atualizar / remover |

### Exemplo de uso

```bash
# criar categoria
curl -X POST http://127.0.0.1:8000/categories \
  -H 'Content-Type: application/json' \
  -d '{"label": "Bolos", "icon": "cake"}'

# criar produto na categoria 1
curl -X POST http://127.0.0.1:8000/products \
  -H 'Content-Type: application/json' \
  -d '{"name": "Bolo de Cenoura", "price": 42.0, "category_id": 1, "stock": 8}'

# categoria com produtos
curl http://127.0.0.1:8000/categories/1/products

# criar usuário e autenticar
curl -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"name": "Ana", "email_address": "ana@example.com", "password": "supersecret"}'

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email_address": "ana@example.com", "password": "supersecret"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl http://127.0.0.1:8000/users/me -H "Authorization: Bearer $TOKEN"
```

## Testes

Os testes usam SQLite em memória (não precisam do Postgres):

```bash
source .venv/bin/activate
pytest -q
```

## Estrutura de pastas

```text
.
├── main.py                  # app FastAPI + lifespan (init_db)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── api/
│   ├── dependencies.py      # get_current_user (JWT)
│   ├── routes/              # endpoints (finos)
│   ├── controllers/         # orquestração HTTP (404/409/403)
│   └── dtos/                # schemas Pydantic (Create/Update/Read)
├── services/                # regras de negócio
├── repositories/            # acesso a dados (SQLAlchemy)
├── models/                  # modelos SQLAlchemy
├── core/                    # config (pydantic-settings) e security (bcrypt/JWT)
├── database/                # Base, engine, get_db, init_db
└── tests/                   # pytest + TestClient (SQLite em memória)
```

## Notas e limitações

- `init_db()` usa `create_all` — adequado para desenvolvimento. Para produção, use **Alembic** (migrations).
- As credenciais padrão (`cakeapi/cakeapi`, `SECRET_KEY` de exemplo) são apenas para desenvolvimento. Troque-as em qualquer ambiente real.
- Senhas são armazenadas com **bcrypt**; autenticação via **JWT** (`Authorization: Bearer <token>`).
- O `.env` não é commitado (ver `.gitignore`); use `.env.example` como referência.
