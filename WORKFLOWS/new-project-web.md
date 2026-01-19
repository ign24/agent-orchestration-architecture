# Workflow: New Project Web

## Objetivo
Crear un proyecto web completo desde cero hasta deploy inicial.

## Pre-requisitos
- [ ] Nombre del proyecto
- [ ] Tipo: landing | dashboard | SaaS | e-commerce
- [ ] Auth requerida? (recomendado para dashboard/SaaS)
- [ ] Cuenta de Vercel (opcional, para deploy)

---

## Flow Diagram

```
┌─────────────────────┐
│ Fase 1: Setup       │
│ Skill: mvp-nextjs   │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ ¿Auth        │
    │ requerida?   │
    └──────┬───────┘
           │
      SÍ   │   NO
    ┌──────┴───────┐
    ▼              │
┌─────────────┐    │
│ Fase 2:     │    │
│ Auth        │    │
│ Skill:      │    │
│ feature-auth│    │
└──────┬──────┘    │
       │           │
       ▼           ▼
┌─────────────────────┐
│ Fase 3: Deploy      │
│ Skill: deploy-vercel│
└─────────────────────┘
```

---

## Fases

### Fase 1: Project Setup
**Skill:** `mvp-nextjs`

**Objetivo:** Crear estructura base del proyecto

**Pasos:**
1. Crear proyecto Next.js 15 con App Router
2. Configurar Tailwind 4
3. Instalar shadcn/ui con componentes base
4. Crear estructura de carpetas
5. Verificar build

**Checkpoint:**
```
✓ Proyecto creado en: [path]
✓ Build pasa sin errores
✓ Dev server funciona en http://localhost:3000

¿Continuar con autenticación? [sí/no/modificar]
```

---

### Fase 2: Autenticación (Condicional)
**Skill:** `feature-auth`
**Condición:** Solo si auth requerida

**Objetivo:** Implementar login/signup con Supabase

**Pasos:**
1. Configurar Supabase client
2. Crear middleware de protección
3. Implementar Server Actions para auth
4. Crear páginas de login/signup
5. Proteger rutas del dashboard

**Pre-requisitos de fase:**
- [ ] Proyecto Supabase creado
- [ ] URL y anon key disponibles

**Checkpoint:**
```
✓ Auth configurada
✓ Login funciona
✓ Rutas protegidas

Variables de entorno configuradas:
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY

¿Continuar con deploy? [sí/no/agregar features]
```

---

### Fase 3: Deploy Inicial
**Skill:** `deploy-vercel`

**Objetivo:** Publicar versión inicial en Vercel

**Pasos:**
1. Verificar build local
2. Preparar variables de entorno
3. Deploy a Vercel
4. Verificar funcionamiento
5. (Opcional) Configurar dominio

**Pre-requisitos de fase:**
- [ ] Build local funciona
- [ ] Variables de entorno listadas
- [ ] Cuenta de Vercel

**Checkpoint Final:**
```
✓ Deploy completado
✓ URL: https://[proyecto].vercel.app
✓ Auth funciona en producción

PROYECTO COMPLETADO

Próximos pasos sugeridos:
1. Agregar features específicas
2. Configurar dominio personalizado
3. Implementar analytics
```

---

## Decisiones Durante el Workflow

### Si NO se requiere auth:
- Saltar Fase 2
- Ir directo a deploy

### Si NO se quiere deploy ahora:
- Terminar después de Fase 1 o 2
- Guardar estado para continuar después

### Si hay errores en alguna fase:
- Ejecutar skill: `debug-systematic`
- Resolver antes de continuar
- No avanzar con errores pendientes

---

## Estado a Persistir

Guardar en `[proyecto]/PROJECT_CONTEXT.md`:

```markdown
## Proyecto: [nombre]
Creado: [fecha]
Tipo: [landing|dashboard|SaaS]

## Stack
- Next.js 15
- React 19
- Tailwind 4
- shadcn/ui
- Supabase (si auth)

## Estado del Workflow
- [x] Fase 1: Setup
- [x] Fase 2: Auth
- [ ] Fase 3: Deploy

## URLs
- Local: http://localhost:3000
- Producción: [pending]

## Variables de Entorno
- NEXT_PUBLIC_SUPABASE_URL: ✓
- NEXT_PUBLIC_SUPABASE_ANON_KEY: ✓

## Próximos Pasos
1. [lista de features pendientes]
```

---

## Estimación de Tiempo

| Fase | Tiempo Estimado |
|------|-----------------|
| Setup | 10-15 min |
| Auth | 15-20 min |
| Deploy | 5-10 min |
| **Total** | **30-45 min** |

---

## Autonomy

**Fases ejecutadas como "delegado":**
- Fase 1: Setup (seguir skill mvp-nextjs)

**Fases ejecutadas como "co-pilot":**
- Fase 2: Auth (confirmar antes de modificar middleware)
- Fase 3: Deploy (confirmar antes de `vercel --prod`)

**Checkpoints obligatorios:**
- Entre cada fase
- Antes de deploy a producción
