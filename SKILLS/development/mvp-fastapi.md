# Skill: MVP FastAPI

## Trigger
- "crear API", "backend Python", "nuevo servicio"
- "proyecto FastAPI", "REST API"

## Context7
Para documentación actualizada:
- `/tiangolo/fastapi` - FastAPI endpoints, dependencies
- `/pydantic/pydantic` - Validación, BaseModel, Settings

Agregar `use context7` cuando necesites ejemplos actualizados.

---

## Pre-requisitos
- [ ] Nombre del proyecto definido
- [ ] Tipo: API simple | servicio ML | microservicio
- [ ] Python 3.11+ instalado
- [ ] Base de datos? (PostgreSQL | SQLite | Supabase | ninguna)

---

## Steps

### 1. Crear estructura de proyecto
```bash
mkdir [nombre] && cd [nombre]
mkdir -p src/{api,models,schemas,services} tests scripts
touch src/__init__.py src/main.py src/config.py src/dependencies.py
touch .env.example .gitignore
```

### 2. Crear pyproject.toml
```toml
[project]
name = "[nombre]"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "httpx>=0.27",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.8",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short"
```

### 3. Crear configuración (src/config.py)
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "[Nombre]"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    # API
    API_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Database (si aplica)
    # DATABASE_URL: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()
```

### 4. Crear app principal (src/main.py)
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.PROJECT_NAME}...")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}


# Importar routers
# from src.api import items
# app.include_router(items.router, prefix=settings.API_PREFIX)
```

### 5. Crear ejemplo de router (src/api/items.py)
```python
from fastapi import APIRouter, HTTPException, status

from src.schemas.item import ItemCreate, ItemResponse, ItemUpdate


router = APIRouter(prefix="/items", tags=["items"])


# In-memory storage (reemplazar con DB)
_items: dict[str, dict] = {}


@router.get("/", response_model=list[ItemResponse])
async def list_items(skip: int = 0, limit: int = 100):
    items = list(_items.values())
    return items[skip : skip + limit]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    return _items[item_id]


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    import uuid
    item_id = str(uuid.uuid4())
    item_data = {"id": item_id, **item.model_dump()}
    _items[item_id] = item_data
    return item_data


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item: ItemUpdate):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.model_dump(exclude_unset=True)
    _items[item_id].update(update_data)
    return _items[item_id]


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
```

### 6. Crear schemas (src/schemas/item.py)
```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)


class ItemResponse(ItemBase):
    id: str
    
    model_config = ConfigDict(from_attributes=True)
```

### 7. Crear .env.example
```bash
# Environment
ENVIRONMENT=development

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Database (si aplica)
# DATABASE_URL=postgresql://user:pass@localhost/db
```

### 8. Crear .gitignore
```
# Env
.env
.env.local

# Python
__pycache__/
*.pyc
.venv/
venv/
dist/
*.egg-info/
.pytest_cache/
.ruff_cache/

# IDE
.vscode/
.idea/
```

### 9. Setup virtual environment e instalar
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Unix
source .venv/bin/activate

pip install -e ".[dev]"
```

### 10. Verificar
```bash
ruff check .
ruff format --check .
uvicorn src.main:app --reload
# Visitar http://localhost:8000/docs
```

---

## Verification
- [ ] `ruff check .` pasa sin errores
- [ ] `uvicorn src.main:app` inicia correctamente
- [ ] `/health` retorna status healthy
- [ ] `/docs` muestra Swagger UI

---

## Output
```
[nombre]/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── api/
│   │   └── items.py
│   ├── models/
│   ├── schemas/
│   │   └── item.py
│   └── services/
├── tests/
├── scripts/
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## Autonomy: delegado

Ejecutar automáticamente sin confirmación excepto:
- Nombre del proyecto
- Si incluir ejemplo de CRUD

Reportar al final con:
- Estructura creada
- Comando para correr: `uvicorn src.main:app --reload`
- URL de docs: `http://localhost:8000/docs`
