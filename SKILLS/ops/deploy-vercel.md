# Skill: Deploy a Vercel

## Trigger
- "deploy", "subir a producción", "publicar"
- "vercel", "deploy frontend"

## Context7
Para documentación actualizada:
- `/vercel/next.js` - Deployment configuration

---

## Pre-requisitos
- [ ] Proyecto Next.js con build funcionando
- [ ] Cuenta de Vercel
- [ ] CLI de Vercel instalado (opcional)
- [ ] Variables de entorno definidas

---

## Steps

### 1. Verificar Build Local
```bash
bun run build
bun run start  # Verificar que funciona
```

### 2. Preparar Variables de Entorno

**Lista de variables necesarias:**
```bash
# .env.local (ejemplo)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_APP_URL=

# Variables server-side (no NEXT_PUBLIC_)
SUPABASE_SERVICE_ROLE_KEY=
```

### 3. Opción A: Deploy via Vercel Dashboard

1. Ir a https://vercel.com/new
2. Importar repositorio de GitHub
3. Configurar:
   - Framework: Next.js (auto-detectado)
   - Build Command: `bun run build`
   - Output Directory: `.next` (default)
4. Agregar Environment Variables
5. Deploy

### 4. Opción B: Deploy via CLI

```bash
# Instalar CLI
bun add -g vercel

# Login
vercel login

# Deploy preview
vercel

# Deploy producción
vercel --prod
```

### 5. Configurar vercel.json (opcional)
```json
{
  "buildCommand": "bun run build",
  "installCommand": "bun install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_APP_URL": "https://[tu-dominio].vercel.app"
  }
}
```

### 6. Configurar Dominio Personalizado

1. En Vercel Dashboard → Project → Settings → Domains
2. Agregar dominio
3. Configurar DNS:
   - A Record: `76.76.21.21`
   - CNAME: `cname.vercel-dns.com`

---

## Checklist Pre-Deploy

### Código
- [ ] `bun run build` pasa sin errores
- [ ] `bun run lint` pasa sin warnings
- [ ] No hay `console.log` en producción
- [ ] No hay secrets hardcodeados

### Variables de Entorno
- [ ] Todas las `NEXT_PUBLIC_*` configuradas en Vercel
- [ ] Variables server-side configuradas
- [ ] URLs apuntan a producción (no localhost)

### SEO/Meta
- [ ] `<title>` y `<meta description>` configurados
- [ ] Open Graph images
- [ ] favicon.ico

### Performance
- [ ] Images optimizadas (usar `next/image`)
- [ ] No hay dependencias innecesarias
- [ ] Bundle size razonable

---

## Verificación Post-Deploy

```bash
# Verificar que la URL funciona
curl -I https://[tu-app].vercel.app

# Verificar build logs en Vercel Dashboard
# Settings → Deployments → [deployment] → Build Logs
```

### Checklist
- [ ] Página principal carga
- [ ] Auth funciona (si aplica)
- [ ] API routes funcionan
- [ ] No hay errores en console
- [ ] Lighthouse score aceptable (>80)

---

## Rollback

Si algo sale mal:
1. Vercel Dashboard → Deployments
2. Encontrar deployment anterior que funcionaba
3. Click en "..." → "Promote to Production"

O via CLI:
```bash
vercel rollback
```

---

## Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| Build falla | Dependencias | Verificar `bun install` local |
| 500 errors | Variables de entorno | Verificar en Vercel Dashboard |
| CORS errors | API URL incorrecta | Verificar `NEXT_PUBLIC_*` |
| Hydration errors | SSR mismatch | Verificar `use client` directives |

---

## Output
- URL de producción: `https://[proyecto].vercel.app`
- Dashboard: `https://vercel.com/[user]/[proyecto]`

---

## Autonomy: asistente

Pedir confirmación antes de:
- Ejecutar `vercel --prod`
- Configurar dominio personalizado
- Modificar variables de entorno en producción

Ejecutar sin confirmación:
- Verificaciones locales
- Deploy preview (no producción)
- Comandos de diagnóstico
