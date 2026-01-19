# WORKFLOWS - Procesos Multi-Step para Agentes

> Workspace: C:\Proyectos
> Actualizado: Enero 2026

Los **Workflows** son procesos complejos que orquestan múltiples skills y requieren coordinación entre pasos. A diferencia de los skills (tareas atómicas), los workflows tienen:
- **Múltiples fases** con checkpoints
- **Decisiones condicionales** basadas en resultados
- **Estado persistente** entre pasos

---

## Cómo Usar Workflows

### Invocación
```
Ejecutar workflow: new-project-web
```

### Diferencia con Skills
| Aspect | Skill | Workflow |
|--------|-------|----------|
| Complejidad | Tarea única | Múltiples tareas |
| Duración | Minutos | Horas/días |
| Checkpoints | Al final | Entre fases |
| Estado | Sin estado | Persistente |

---

## Workflows Disponibles

### Development

| Workflow | Descripción | Skills Involucrados |
|----------|-------------|---------------------|
| [new-project-web](new-project-web.md) | Crear proyecto web completo | mvp-nextjs, feature-auth, deploy-vercel |
| [new-project-api](new-project-api.md) | Crear API backend completa | mvp-fastapi |

### ML/CV

| Workflow | Descripción | Skills Involucrados |
|----------|-------------|---------------------|
| [ml-experiment](ml-experiment.md) | Ciclo completo de experimentación | dataset-prep, training-pipeline, model-evaluation |
| [cv-project-setup](cv-project-setup.md) | Setup proyecto CV desde cero | yolo-detection, dataset-prep |

---

## Estructura de un Workflow

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

---

## Checkpoints y Human-in-the-Loop

Los workflows incluyen checkpoints donde el agente debe:
1. Mostrar resumen del progreso
2. Pedir confirmación para continuar
3. Ofrecer opciones si hay decisiones

Ejemplo:
```
CHECKPOINT: Fase 1 completada

Progreso:
- [x] Proyecto creado
- [x] shadcn instalado
- [ ] Auth pendiente

Próxima fase: Implementar autenticación

¿Continuar con auth? (sí/no/modificar plan)
```

---

## Persistencia de Estado

Al final de cada workflow o sesión, actualizar `PROJECT_CONTEXT.md`:

```markdown
## Workflow: new-project-web
Estado: Fase 2/3 completada
Última actualización: 2026-01-17

### Completado
- [x] Proyecto Next.js creado
- [x] shadcn/ui configurado

### Pendiente
- [ ] Implementar auth
- [ ] Deploy inicial

### Decisiones
- Auth: Supabase (elegido por usuario)
- Deploy: Vercel (default)
```
