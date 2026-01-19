# AGENTS.md - AI Engineering Fullstack Workspace

> Compatible con: Claude Code, Cursor, OpenCode, Codex, GitHub Copilot, Windsurf
> Perfil: AI Engineering Fullstack / Indie Hacker
> Actualizado: Enero 2026

---

## Project Overview

Workspace para AI/ML engineering, desarrollo fullstack, y MVPs rápidos.
**Focus:** Computer vision, modelos multimodales, aplicaciones web modernas, y experimentación rápida.

---

## Quick Reference

```bash
# Python - Testing & Linting
pytest -x -v                    # Stop on first failure
ruff check .                    # Lint
ruff format .                   # Format
ruff check --fix .              # Auto-fix

# Frontend - Bun + Next.js
bun create next-app             # Nuevo proyecto
bun install                     # Instalar deps
bun run dev                     # Dev server
bun run build                   # Build prod
bun run lint                    # ESLint

# Git
git status && git diff          # Ver cambios
git add -p                      # Stage interactivo
```

---

## Stack Reference (Enero 2026)

### Frontend
| Tech | Version | Uso |
|------|---------|-----|
| Next.js | 15.x | Framework React fullstack |
| React | 19.x | UI library |
| Tailwind CSS | 4.x | Utility-first CSS |
| shadcn/ui | latest | Componentes accesibles |
| Framer Motion | 11.x | Animaciones |

### Backend
| Tech | Version | Uso |
|------|---------|-----|
| FastAPI | 0.115+ | APIs Python |
| Pydantic | 2.x | Validación de datos |
| Supabase | latest | Auth, DB, Storage (MVP rápido) |
| SQLModel | 0.0.22+ | ORM + Pydantic |

### ML/CV
| Tech | Version | Uso |
|------|---------|-----|
| PyTorch | 2.5+ | Deep learning |
| Ultralytics | 8.3+ | YOLO detection/segmentation |
| Supervision | 0.25+ | CV utilities (Roboflow) |
| Transformers | 4.47+ | HuggingFace models |

### Package Managers
| Lang | Tool | Comando |
|------|------|---------|
| Python | pip | `pip install -e ".[dev]"` |
| Node | bun | `bun install` |

---

## MVP Scaffold Commands

### Next.js + shadcn (recomendado para UI)
```bash
# Crear proyecto
bun create next-app@latest my-app --typescript --tailwind --eslint --app --src-dir

# Agregar shadcn
cd my-app
bunx shadcn@latest init
bunx shadcn@latest add button card input  # componentes que necesites
```

### FastAPI Backend
```bash
# Estructura básica
mkdir -p src/{api,models,services} tests
touch src/__init__.py src/main.py src/config.py

# pyproject.toml mínimo
# Ver sección "Python Project Setup" abajo
```

### Supabase (MVP rápido)
```bash
# Instalar CLI
bun add -g supabase

# Iniciar proyecto local
supabase init
supabase start

# En frontend
bun add @supabase/supabase-js
```

---

## Directory Structures

### Python Project
```
project/
├── AGENTS.md
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── config.py         # Settings con Pydantic
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   └── api/              # FastAPI routes
├── tests/
├── scripts/              # CLI tools
└── .env.example
```

### Next.js Project
```
project/
├── AGENTS.md
├── src/
│   ├── app/              # App router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── (routes)/
│   ├── components/
│   │   ├── ui/           # shadcn components
│   │   └── custom/       # Tu código
│   ├── lib/              # Utils, supabase client
│   └── hooks/            # Custom hooks
├── public/
└── .env.local
```

### ML/CV Project
```
project/
├── AGENTS.md
├── notebooks/            # Exploración (no prod)
├── src/
│   ├── models/           # Model wrappers
│   ├── data/             # Data loading
│   ├── evaluation/       # Métricas
│   └── utils/
├── scripts/              # CLI, inference
├── configs/              # YAML configs
├── tests/
└── outputs/              # Artifacts (gitignored)
```

---

## Coding Conventions

### Python Style
- **Type hints**: Obligatorios en funciones públicas
- **Modern syntax**: `list[str]` no `List[str]`, `dict[str, Any]` no `Dict`
- **Docstrings**: Google style, solo cuando agregan valor
- **Line length**: 100 chars
- **Formatter**: ruff

```python
def process_data(
    items: list[dict[str, Any]],
    limit: int = 100,
    *,
    validate: bool = True
) -> list[ProcessedItem]:
    """Process items with optional validation.
    
    Args:
        items: Raw data items
        limit: Max items to process
        validate: Whether to validate output
        
    Returns:
        List of processed items
    """
    ...
```

### TypeScript/React Style
- **Strict mode**: Siempre habilitado
- **Components**: Function components con arrow functions
- **Props**: Interface separada o inline para simple
- **Hooks**: Prefijo `use`

```tsx
interface CardProps {
  title: string;
  description?: string;
  onClick?: () => void;
}

const Card = ({ title, description, onClick }: CardProps) => {
  return (
    <div className="rounded-lg border p-4" onClick={onClick}>
      <h3 className="font-semibold">{title}</h3>
      {description && <p className="text-muted-foreground">{description}</p>}
    </div>
  );
};
```

### Philosophy
- **Hacelo andar primero**, optimizá después
- **Explícito > clever** para lógica de negocio
- **No premature optimization** - profile first
- **Ship fast, iterate** - MVP mindset

---

## Testing Requirements

### Python
```bash
pytest -x -v                    # Stop on first failure
pytest tests/ --tb=short        # All tests
pytest -k "test_api"            # Filter by name
```

### Frontend
```bash
bun run test                    # Jest/Vitest
bun run test:e2e                # Playwright (si está configurado)
```

**Mínimo:** Smoke tests que verifiquen que todo corre.

---

## Git Workflow

- `main` branch protegido
- Feature branches: `feat/description`, `fix/description`
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`

```bash
# Ejemplo
git checkout -b feat/user-auth
# ... trabajo ...
git commit -m "feat: add user authentication with Supabase"
```

---

## Agent Behavior Rules

### Core Philosophy

```
PLANIFICAR → CONFIRMAR → EJECUTAR → VERIFICAR
```

**Los agentes son asistentes, no autónomos.** Las decisiones importantes las toma el humano.

### Confirmation Required

SIEMPRE pedir confirmación ANTES de:
- [ ] Eliminar archivos o directorios
- [ ] Modificar archivos fuera del scope del task
- [ ] Ejecutar comandos con `sudo` o admin
- [ ] Instalar dependencias globales
- [ ] Git push/merge a `main`
- [ ] Cualquier operación irreversible
- [ ] Deploy a producción

### Pre-approved Commands (no confirmation needed)

```bash
# Read operations
ls, cat, head, tail, grep, find, tree, wc
python --version, pip list, pip show, which
bun --version, node --version

# Testing & Linting
pytest, ruff check, ruff format --check
bun run lint, bun run test, bun run build

# Git (read-only)
git status, git log, git diff, git branch, git show
```

### Planning Requirement

Para tareas complejas (>30 min), crear plan antes de ejecutar:

```markdown
## Plan: [Task Name]

### Objetivo
[Una oración clara]

### Pasos
1. [ ] Paso 1
2. [ ] Paso 2
3. [ ] Paso 3

### Archivos a modificar
- path/to/file.py

### Riesgos
- [Si aplica]

Esperando confirmación...
```

### Post-Task Checklist

Después de cada tarea, verificar:

```bash
# Python
ruff check . && ruff format --check . && pytest -x

# Frontend
bun run lint && bun run build

# Secrets check
grep -r "API_KEY\|SECRET\|PASSWORD" src/ --include="*.py" --include="*.ts"
```

Solo marcar como "listo" cuando TODO pase.

---

## ML/CV Specific Guidelines

### Experiment Tracking

```python
config = {
    "model": "yolo11n",
    "dataset": "custom_v2",
    "timestamp": datetime.now().isoformat(),
    "git_hash": get_git_hash(),
}

results = evaluate(model, dataset)
save_results(results, config, f"outputs/{config['model']}_{config['timestamp']}")
```

### Output Structure

```
outputs/
├── experiments/
│   └── yolo11n_20260116/
│       ├── config.yaml
│       ├── metrics.csv
│       ├── summary.json
│       └── errors.log
└── models/
    └── checkpoints/
```

### Model Evaluation Checklist

Siempre incluir:
- [ ] Baseline (modelo anterior o conocido)
- [ ] Métricas estándar del dominio
- [ ] Tiempo de inferencia
- [ ] Uso de memoria/GPU

---

## Web/MVP Guidelines

### Supabase Quick Setup

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);
```

### API Routes Pattern (Next.js 15)

```typescript
// app/api/items/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const data = await fetchItems();
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const body = await request.json();
  const item = await createItem(body);
  return NextResponse.json(item, { status: 201 });
}
```

### FastAPI Pattern

```python
# src/api/items.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["items"])

class ItemCreate(BaseModel):
    name: str
    description: str | None = None

@router.get("/")
async def list_items():
    return await get_all_items()

@router.post("/", status_code=201)
async def create_item(item: ItemCreate):
    return await create_new_item(item)
```

---

## Python Project Setup

### pyproject.toml Template

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn>=0.32",
    "pydantic>=2.0",
    "httpx>=0.27",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

---

## Environment Templates

### .env.example (General)
```bash
# API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### .gitignore Essentials
```
# Env
.env
.env.local
.env*.local

# Python
__pycache__/
*.pyc
.venv/
dist/
*.egg-info/

# Node
node_modules/
.next/
.turbo/

# IDE
.vscode/
.idea/

# Output
outputs/
*.log
```

---

## Critical Rules

1. **NEVER** commit secrets/API keys - usar .env
2. **NEVER** push a main sin tests passing
3. **ALWAYS** run lint antes de commit
4. **Notebooks son para exploración** - extraer a src/ cuando el pattern sea sólido
5. **Ship fast** - MVP primero, perfección después

---

## Error Handling

Cuando algo falla, reportar con contexto:

```
Error: [descripción corta]
Archivo: [path]
Causa probable: [hipótesis]
Opciones:
   A) [opción 1]
   B) [opción 2]

¿Cuál preferís?
```

No reintentar ciegamente - analizar el error primero.

---

## Project-Specific Overrides

Si un proyecto necesita reglas diferentes, editar el AGENTS.md local.
Las reglas del proyecto sobreescriben las globales.

---

## Skills & Workflows System

### Skills (Tareas Atómicas)

Los skills son tareas reutilizables definidas en `/your/workspace\SKILLS\`.

**Invocar:** `Ejecutar skill: [nombre]`

#### Skills Registry

| Skill | Descripción | Autonomy |
|-------|-------------|----------|
| `mvp-nextjs` | Crear proyecto Next.js 15 + shadcn | delegado |
| `mvp-fastapi` | Crear API FastAPI + Pydantic | delegado |
| `feature-auth` | Auth con Supabase | co-pilot |
| `yolo-detection` | Setup detección YOLO | delegado |
| `training-pipeline` | Pipeline de training ML | co-pilot |
| `dataset-prep` | Preparar dataset CV | co-pilot |
| `model-evaluation` | Evaluar modelo vs baseline | delegado |
| `debug-systematic` | Debugging con metodología | co-pilot |
| `deploy-vercel` | Deploy a Vercel | asistente |

### Workflows (Procesos Multi-Step)

Los workflows orquestan múltiples skills con checkpoints.

**Invocar:** `Ejecutar workflow: [nombre]`

#### Workflows Registry

| Workflow | Descripción | Skills |
|----------|-------------|--------|
| `new-project-web` | Proyecto web completo | mvp-nextjs → feature-auth → deploy-vercel |
| `ml-experiment` | Ciclo de experimentación ML | dataset-prep → training-pipeline → model-evaluation |

---

## Routing (Auto-detection)

El agente detecta automáticamente qué skill/workflow usar:

| Input Pattern | Route To |
|---------------|----------|
| "crear proyecto web/MVP/landing" | Workflow: `new-project-web` |
| "crear API/backend Python" | Skill: `mvp-fastapi` |
| "agregar auth/login" | Skill: `feature-auth` |
| "detectar objetos/YOLO" | Skill: `yolo-detection` |
| "entrenar modelo" | Skill: `training-pipeline` |
| "preparar dataset" | Skill: `dataset-prep` |
| "evaluar modelo" | Skill: `model-evaluation` |
| "bug/error/no funciona" | Skill: `debug-systematic` |
| "deploy/publicar" | Skill: `deploy-vercel` |
| "experimento ML" | Workflow: `ml-experiment` |

---

## Autonomy Levels

| Level | Comportamiento | Cuándo |
|-------|---------------|--------|
| **delegado** | Ejecuta sin confirmación | Tareas bien definidas, bajo riesgo |
| **co-pilot** | Confirma antes de cambios grandes | Tareas complejas |
| **asistente** | Confirma cada paso | Operaciones críticas |

---

## Context7 Integration

Usar Context7 MCP para documentación actualizada del stack.

### Library IDs
```
Next.js:      /vercel/next.js
React:        /facebook/react
Tailwind:     /tailwindlabs/tailwindcss
shadcn/ui:    /shadcn-ui/ui
FastAPI:      /tiangolo/fastapi
Pydantic:     /pydantic/pydantic
Supabase:     /supabase/supabase
PyTorch:      /pytorch/pytorch
Ultralytics:  /ultralytics/ultralytics
Supervision:  /roboflow/supervision
```

### Uso
Agregar `use context7` al prompt, o invocar:
```
1. resolve-library-id("fastapi")
2. query-docs("/tiangolo/fastapi", "dependency injection")
```

---

## Project Context

Cada proyecto debe tener un `PROJECT_CONTEXT.md` en su raíz.

**Template:** `/your/workspace\TEMPLATES\PROJECT_CONTEXT.md`

### Al Iniciar Sesión
1. Leer `PROJECT_CONTEXT.md`
2. Ver última sesión y TODOs
3. Preguntar si continuar o cambiar foco

### Al Terminar Sesión
1. Actualizar `PROJECT_CONTEXT.md`:
   - Qué se completó
   - Qué quedó pendiente
   - Decisiones tomadas
2. Si ML/CV: actualizar baseline si mejoró
