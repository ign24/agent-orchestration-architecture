# Skill: MVP Next.js

## Trigger
- "crear proyecto web", "nuevo MVP", "landing page", "dashboard"
- "proyecto Next.js", "app React"

## Context7
Para documentación actualizada:
- `/vercel/next.js` - Next.js 15 APIs, App Router
- `/facebook/react` - React 19 hooks, Server Components
- `/tailwindlabs/tailwindcss` - Tailwind 4 utilities
- `/shadcn-ui/ui` - Componentes accesibles

Agregar `use context7` cuando necesites ejemplos actualizados.

---

## Pre-requisitos
- [ ] Nombre del proyecto definido
- [ ] Tipo: landing | dashboard | SaaS | e-commerce
- [ ] Auth requerida? (si → ejecutar `feature-auth` después)
- [ ] Bun instalado (`bun --version`)

---

## Steps

### 1. Crear proyecto base
```bash
bun create next-app@latest [nombre] --typescript --tailwind --eslint --app --src-dir
cd [nombre]
```

### 2. Inicializar shadcn/ui
```bash
bunx shadcn@latest init -d
```

### 3. Agregar componentes base
```bash
bunx shadcn@latest add button card input form
bunx shadcn@latest add dropdown-menu dialog sheet
bunx shadcn@latest add table tabs toast
```

### 4. Crear estructura de carpetas
```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   └── (routes)/        # Rutas agrupadas
├── components/
│   ├── ui/              # shadcn (auto-generado)
│   └── custom/          # Componentes propios
├── lib/
│   ├── utils.ts         # cn() ya incluido
│   └── supabase/        # Si auth requerida
└── hooks/               # Custom hooks
```

### 5. Configurar layout base
```tsx
// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "[Nombre del Proyecto]",
  description: "[Descripción]",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

### 6. Crear página inicial según tipo

**Landing:**
```tsx
// src/app/page.tsx
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <main className="min-h-screen">
      <section className="container mx-auto py-24 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          [Título Principal]
        </h1>
        <p className="mt-6 text-lg text-muted-foreground">
          [Descripción del producto]
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <Button size="lg">Comenzar</Button>
          <Button variant="outline" size="lg">Saber más</Button>
        </div>
      </section>
    </main>
  );
}
```

**Dashboard:**
```tsx
// src/app/page.tsx - redirigir a dashboard
import { redirect } from "next/navigation";
export default function Home() {
  redirect("/dashboard");
}

// src/app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <div className="container py-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      {/* Contenido */}
    </div>
  );
}
```

### 7. Configurar .env.local
```bash
# .env.local
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Si usa Supabase (agregar después de feature-auth)
# NEXT_PUBLIC_SUPABASE_URL=
# NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

### 8. Verificar build
```bash
bun run build
bun run lint
```

---

## Post-Steps Opcionales

### Si requiere Auth
```
Ejecutar skill: feature-auth
```

### Si requiere API
```
Ejecutar skill: feature-crud para cada entidad
```

---

## Verification
- [ ] `bun run build` pasa sin errores
- [ ] `bun run lint` pasa sin warnings
- [ ] Página inicial renderiza correctamente
- [ ] Componentes shadcn funcionan

---

## Output
```
[nombre]/
├── src/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── hooks/
├── public/
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── .env.local
```

---

## Autonomy: delegado

Ejecutar automáticamente sin confirmación excepto:
- Nombre del proyecto (preguntar si no está claro)
- Tipo de proyecto (preguntar si no está claro)
- Si auth es requerida (preguntar)

Reportar al final con:
- Estructura creada
- Comandos para correr el proyecto
- Próximos pasos sugeridos
