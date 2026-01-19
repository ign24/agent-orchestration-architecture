# Agent System Architecture - Documentación Completa

> Workspace: C:\Proyectos
> Perfil: AI Engineering Fullstack / Indie Hacker
> Creado: Enero 2026
> Última actualización: 2026-01-17

---

## Visión General

Sistema de agentes, skills y workflows diseñado para:
- **Maximizar productividad** en desarrollo fullstack y ML/CV
- **Mantener contexto** entre sesiones de trabajo
- **Automatizar tareas repetitivas** sin perder control
- **Escalar conocimiento** con documentación actualizada vía Context7

**Filosofía:** PLANIFICAR → CONFIRMAR → EJECUTAR → VERIFICAR

---

## Estructura del Sistema

```
C:\Proyectos\
│
├── .claude/
│   └── CLAUDE.md                    # Config global del agente
│
├── AGENTS.md                           # Reglas globales + routing
│
├── PATTERNS.md                         # Patrones de código preferidos
│
├── STACK_RECOMMENDATIONS.md              # Tech stack y dependencias
│
├── SKILLS/                             # Tareas atómicas reutilizables
│   ├── README.md                      # Índice y guía de uso
│   ├── development/
│   │   ├── mvp-nextjs.md            # Crear proyecto Next.js 15
│   │   ├── mvp-fastapi.md           # Crear API FastAPI
│   │   ├── feature-auth.md           # Auth con Supabase
│   │   └── feature-crud.md           # CRUD genérico
│   ├── ml-cv/
│   │   ├── yolo-detection.md        # Setup detección YOLO
│   │   ├── training-pipeline.md       # Training ML
│   │   ├── dataset-prep.md          # Preparar dataset
│   │   └── model-evaluation.md      # Evaluar modelo
│   └── ops/
│       ├── debug-systematic.md      # Debugging metodológico
│       └── deploy-vercel.md          # Deploy a Vercel
│
├── WORKFLOWS/                          # Procesos multi-step
│   ├── README.md                      # Índice de workflows
│   ├── new-project-web.md              # MVP web completo
│   └── ml-experiment.md               # Ciclo experimentación ML
│
├── TEMPLATES/                          # Templates para proyectos
│   └── PROJECT_CONTEXT.md            # Template de contexto por proyecto
│
└── [proyecto]/
    ├── AGENTS.md                       # Override específico (si aplica)
    └── PROJECT_CONTEXT.md            # Memoria del proyecto
```

---

## Componentes del Sistema

### 1. Skills (Tareas Atómicas)

**Definición:** Tareas autónomas, bien definidas, que pueden ejecutarse repetidamente sin modificaciones.

**Estructura de un Skill:**
```markdown
# Skill: [nombre]

## Trigger
- Palabras clave que activan este skill
- Ejemplos de prompts

## Context7
- Library IDs relevantes para `use context7`

## Pre-requisitos
- [ ] Requisito 1
- [ ] Requisito 2

## Steps
1. Paso 1
2. Paso 2
3. Paso 3

## Verification
- [ ] Check 1
- [ ] Check 2

## Autonomy: [delegado|co-pilot|asistente]
Descripción de cuándo pedir confirmación.
```

**Autonomy Levels:**

| Level | Comportamiento | Ejemplos |
|-------|---------------|-----------|
| **delegado** | Ejecuta sin confirmación | Crear estructura, instalar deps, escribir boilerplate |
| **co-pilot** | Confirma antes de cambios grandes | Modificar middleware, configurar DB, cambios de arquitectura |
| **asistente** | Confirma cada paso | Deploy producción, operaciones destructivas |

**Skills Disponibles:**

| Categoría | Skills | Autonomy |
|-----------|---------|----------|
| Development | mvp-nextjs, mvp-fastapi, feature-auth, feature-crud | mix |
| ML/CV | yolo-detection, training-pipeline, dataset-prep, model-evaluation | mix |
| Ops | debug-systematic, deploy-vercel, test-coverage | mix |

---

### 2. Workflows (Procesos Multi-Step)

**Definición:** Procesos complejos que coordinan múltiples skills con checkpoints intermedios.

**Estructura de un Workflow:**
```markdown
# Workflow: [nombre]

## Objetivo
[Una oración clara del resultado esperado]

## Pre-requisitos
[Qué se necesita antes de empezar]

## Fases

### Fase 1: [Nombre]
- Skill: [skill a ejecutar]
- Checkpoint: [qué verificar antes de continuar]

### Fase 2: [Nombre]
...

## Decisiones
[Condiciones que afectan el flujo]

## Estado a Persistir
[Qué guardar en PROJECT_CONTEXT.md]
```

**Diferencias Clave vs Skills:**

| Aspecto | Skill | Workflow |
|---------|-------|-----------|
| Complejidad | Tarea única | Múltiples tareas coordinadas |
| Duración | Minutos | Horas/días |
| Checkpoints | Al final | Entre fases |
| Estado | Sin estado | Persistente entre fases |

**Workflows Disponibles:**

| Workflow | Skills Involucrados | Estimación |
|----------|---------------------|-------------|
| new-project-web | mvp-nextjs → feature-auth → deploy-vercel | 30-45 min |
| ml-experiment | dataset-prep → training-pipeline → model-evaluation | 1-4 horas |

---

### 3. Routing Automático

**Mecanismo:** El agente detecta automáticamente qué skill/workflow usar basado en el input del usuario.

**Tabla de Routing:**

| Input Pattern | Route To | Tipo |
|---------------|----------|------|
| "crear proyecto web/MVP/landing" | Workflow: new-project-web | Workflow |
| "proyecto Next.js" | Skill: mvp-nextjs | Skill |
| "crear API/backend Python" | Skill: mvp-fastapi | Skill |
| "agregar autenticación/login" | Skill: feature-auth | Skill |
| "detectar objetos/YOLO/ultralytics" | Skill: yolo-detection | Skill |
| "entrenar modelo/training" | Skill: training-pipeline | Skill |
| "preparar dataset" | Skill: dataset-prep | Skill |
| "evaluar modelo/métricas" | Skill: model-evaluation | Skill |
| "bug/error/no funciona" | Skill: debug-systematic | Skill |
| "deploy/publicar" | Skill: deploy-vercel | Skill |
| "experimento ML/ciclo" | Workflow: ml-experiment | Workflow |

**Implementación:** Definido en `AGENTS.md` sección "Routing".

---

### 4. Context7 Integration

**Propósito:** Proveer documentación siempre actualizada de las librerías del stack.

**Library IDs del Stack:**

```
Frontend:
  Next.js 15:      /vercel/next.js
  React 19:        /facebook/react
  Tailwind 4:       /tailwindlabs/tailwindcss
  shadcn/ui:        /shadcn-ui/ui

Backend:
  FastAPI:          /tiangolo/fastapi
  Pydantic v2:       /pydantic/pydantic
  Supabase:         /supabase/supabase

ML/CV:
  PyTorch:          /pytorch/pytorch
  Ultralytics:       /ultralytics/ultralytics
  Supervision:       /roboflow/supervision
```

**Uso:**
```
# Automático en el prompt
"Crear un endpoint FastAPI con validación Pydantic. use context7"

# Manual invocando tools
1. resolve-library-id("fastapi")
2. query-docs("/tiangolo/fastapi", "dependency injection")
```

**Configuración:**
- MCP server activo en `CLAUDE.md`
- API key opcional para rate limits mayores

---

### 5. MCP Servers

**Servers Activos:**

| MCP | Propósito | Estado |
|-----|----------|--------|
| context7 | Documentación actualizada librerías | ✓ Activo |
| memory | Persistencia entre sesiones | ✓ Activo |
| sequential-thinking | Razonamiento problemas complejos | ✓ Activo |

**Configuración:** Definida en `CLAUDE.md` sección "MCP Servers Activos".

---

## Ciclo de Vida de un Proyecto

### Inicio de Proyecto

1. **Crear proyecto** con `mvp-nextjs` o `mvp-fastapi`
2. **Crear PROJECT_CONTEXT.md** desde template
3. **Definir stack y variables**
4. **Agregar skills específicos del proyecto** en `PROJECT_CONTEXT.md`

### Sesiones de Trabajo

**Al iniciar cada sesión:**

1. Leer `PROJECT_CONTEXT.md`
2. Ver última sesión
3. Identificar TODOs pendientes
4. Preguntar si continuar o nueva tarea

**Durante la sesión:**

1. Usar skills/workflows según routing automático
2. Checkpoints requieren confirmación humana
3. Documentar decisiones importantes

**Al terminar sesión:**

1. Actualizar `PROJECT_CONTEXT.md`:
   - Qué se completó
   - Qué quedó pendiente
   - Decisiones tomadas
2. Si es ML/CV: actualizar baseline si mejoró

---

## Flujos de Trabajo Comunes

### Flujo 1: Nuevo Proyecto Web

```
Usuario: "Quiero crear un SaaS de gestión de tareas"
       ↓
Agente detecta: "crear proyecto web"
       ↓
Ejecutar workflow: new-project-web
       ├─► Fase 1: Setup (mvp-nextjs)
       │   └─► Crear Next.js + shadcn
       ├─► Fase 2: Auth (feature-auth) [opcional]
       │   └─► Supabase auth
       └─► Fase 3: Deploy (deploy-vercel)
           └─► Vercel deploy
       ↓
Output: URL de producción
```

### Flujo 2: Experimento ML

```
Usuario: "Quiero entrenar un modelo para detectar defectos en metal"
       ↓
Agente detecta: "experimento ML"
       ↓
Ejecutar workflow: ml-experiment
       ├─► Fase 1: Definir hipótesis
       ├─► Fase 2: Dataset prep (dataset-prep)
       │   └─► Convertir a YOLO format
       ├─► Fase 3: Training (training-pipeline)
       │   └─► Entrenar con config
       ├─► Fase 4: Evaluation (model-evaluation)
       │   └─► Comparar vs baseline
       └─► Fase 5: Documentar
           └─► Guardar métricas
       ↓
Output: Modelo entrenado + métricas documentadas
```

### Flujo 3: Debugging

```
Usuario: "El endpoint /api/users no funciona, da 500"
       ↓
Agente detecta: "bug"
       ↓
Ejecutar skill: debug-systematic
       ├─► Fase 1: Recopilar info
       │   └─► Logs, traceback, pasos para reproducir
       ├─► Fase 2: Diagnosticar
       │   └─► Verificar imports, variables, llamadas
       ├─► Fase 3: Implementar fix
       │   └─► Modificar código
       └─► Fase 4: Verificar
           └─► Tests pasan
       ↓
Output: Bug resuelto
```

---

## Mejoras Futuras

### Corto Plazo (Próximas 2-4 semanas)

- [ ] Agregar más skills de desarrollo
  - [ ] feature-crud (agregado al registry)
  - [ ] feature-testing (setup tests)
  - [ ] refator-component (refactorización React)

- [ ] Expandir workflows
  - [ ] new-project-api (FastAPI completo)
  - [ ] cv-project-setup (proyecto CV desde cero)

- [ ] Integración con Smithery
  - [ ] Skills compartidos públicamente
  - [ ] Versionar skills con tags

### Mediano Plazo (1-3 meses)

- [ ] Crear MCP server custom
  - [ ] Para búsqueda en `SKILLS/` y `WORKFLOWS/`
  - [ ] Para lectura de `PROJECT_CONTEXT.md`

- [ ] Dashboard de progreso
  - [ ] Ver todos los proyectos y sus estados
  - [ ] Historial de experimentos ML

- [ ] Sistema de métricas
  - [ ] Tracking de tiempo por skill/workflow
  - [ ] Mejoras sugeridas automáticamente

---

## Ventajas del Sistema

| Aspecto | Sin Sistema | Con Sistema |
|----------|-------------|-------------|
| **Consistencia** | Depende de memoria del usuario | Skills/workflows versionados en git |
| **Velocidad** | Repetir instrucciones cada vez | Skills ejecutan pasos pre-definidos |
| **Calidad** | Variante según contexto del modelo | Skills incluyen best practices |
| **Documentación** | Dispersa en chats | Centralizada en `PROJECT_CONTEXT.md` |
| **Escalabilidad** | Difícil agregar nuevo conocimiento | Fácil crear nuevos skills |
| **Contexto** | Se pierde entre sesiones | `PROJECT_CONTEXT.md` + MCP memory |
| **Colaboración** | Compartir contexto manualmente | Skills compartibles entre proyectos |

---

## Archivos de Configuración

### C:\Proyectos\AGENTS.md
Reglas globales, routing table, registry de skills/workflows.

### C:\Users\nnznn\.claude\CLAUDE.md
Config global del agente, MCP servers, comandos rápidos.

### [proyecto]\PROJECT_CONTEXT.md
Contexto específico del proyecto (TODOs, decisiones, baseline).

---

## Métricas de Éxito

**Objetivos del sistema:**

1. ✅ Reducir setup time en **70%**
   - De 15-20 min → 5-10 min para proyecto base

2. ✅ Aumentar consistencia de código en **60%**
   - Patrones aplicados automáticamente vía skills

3. ✅ Mantener contexto entre sesiones
   - `PROJECT_CONTEXT.md` + MCP memory

4. ✅ Documentación siempre actualizada
   - Context7 MCP para APIs librerías

5. ✅ Escalable y mantenible
   - Fácil agregar nuevos skills/workflows

---

## Soporte y Mantenimiento

### Agregar un Nuevo Skill

1. Copiar template de `SKILLS/README.md`
2. Seguir estructura de skill
3. Agregar a `SKILLS/registry` en README
4. Actualizar routing en `AGENTS.md`
5. Commit cambios

### Actualizar un Skill Existente

1. Leer el skill actual
2. Mejorar pasos/code examples
3. Actualizar secciones de Context7 si aplica
4. Commit cambios

### Reportar un Problema

Si un skill/workflow tiene issues:
1. Documentar en `PROJECT_CONTEXT.md` del proyecto
2. Crear issue en repo (si aplica)
3. Probar workaround o parche manual
4. Reportar para corrección futura

---

## Referencias

**Principios de Diseño:**
- Anthropic Building Effective Agents: https://www.anthropic.com/research/building-effective-agents
- Model Context Protocol: https://modelcontextprotocol.io
- Context7: https://context7.com
- Smithery Skills: https://smithery.ai/skills

**Stack 2026:**
- Next.js 15, React 19, Tailwind 4
- FastAPI, Pydantic v2, Supabase
- PyTorch 2.5+, Ultralytics 8.3+, Supervision 0.25+

---

**Fin de Documentación**

Este documento describe la arquitectura completa del sistema de agentes implementado.
Para comenzar a usarlo, simplemente decirle al agente: "Ejecutar skill: [nombre]" o "Ejecutar workflow: [nombre]".
