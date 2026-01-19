# PATTERNS.md - Patrones Preferidos

> Perfil: AI Engineering Fullstack / Indie Hacker
> Stack: Next.js 15, React 19, Tailwind 4, shadcn/ui, FastAPI, Supabase
> Actualizado: Enero 2026

Este archivo documenta los patrones preferidos para desarrollo rápido de MVPs y proyectos fullstack.

---

## Auth con Supabase

### Setup del Cliente

```typescript
// lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'

export const createClient = () =>
  createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
```

```typescript
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export const createClient = async () => {
  const cookieStore = await cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // Server Component - ignore
          }
        },
      },
    }
  )
}
```

### Middleware de Protección

```typescript
// middleware.ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          response = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  // Rutas protegidas
  if (!user && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api/webhook).*)'],
}
```

### Auth Actions

```typescript
// app/actions/auth.ts
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

export async function signIn(formData: FormData) {
  const supabase = await createClient()

  const { error } = await supabase.auth.signInWithPassword({
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  })

  if (error) {
    return { error: error.message }
  }

  revalidatePath('/', 'layout')
  redirect('/dashboard')
}

export async function signUp(formData: FormData) {
  const supabase = await createClient()

  const { error } = await supabase.auth.signUp({
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  })

  if (error) {
    return { error: error.message }
  }

  revalidatePath('/', 'layout')
  redirect('/verify-email')
}

export async function signOut() {
  const supabase = await createClient()
  await supabase.auth.signOut()
  redirect('/login')
}
```

---

## API Routes (Next.js 15)

### Route Handler Básico

```typescript
// app/api/items/route.ts
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET() {
  const supabase = await createClient()
  
  const { data, error } = await supabase
    .from('items')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json(data)
}

export async function POST(request: Request) {
  const supabase = await createClient()
  const body = await request.json()

  const { data, error } = await supabase
    .from('items')
    .insert(body)
    .select()
    .single()

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 400 })
  }

  return NextResponse.json(data, { status: 201 })
}
```

### Con Validación (Zod)

```typescript
// app/api/items/route.ts
import { NextResponse } from 'next/server'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/server'

const ItemSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  price: z.number().positive().optional(),
})

export async function POST(request: Request) {
  const supabase = await createClient()
  
  // Validar body
  const body = await request.json()
  const result = ItemSchema.safeParse(body)
  
  if (!result.success) {
    return NextResponse.json(
      { error: 'Validation failed', details: result.error.flatten() },
      { status: 400 }
    )
  }

  const { data, error } = await supabase
    .from('items')
    .insert(result.data)
    .select()
    .single()

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json(data, { status: 201 })
}
```

### Dynamic Route

```typescript
// app/api/items/[id]/route.ts
import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

type Params = { params: Promise<{ id: string }> }

export async function GET(request: Request, { params }: Params) {
  const { id } = await params
  const supabase = await createClient()

  const { data, error } = await supabase
    .from('items')
    .select('*')
    .eq('id', id)
    .single()

  if (error) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  return NextResponse.json(data)
}

export async function DELETE(request: Request, { params }: Params) {
  const { id } = await params
  const supabase = await createClient()

  const { error } = await supabase
    .from('items')
    .delete()
    .eq('id', id)

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }

  return NextResponse.json({ success: true })
}
```

---

## FastAPI Backend

### Estructura de Proyecto

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── item.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── item.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── items.py
│   └── services/
│       ├── __init__.py
│       └── item_service.py
├── tests/
├── pyproject.toml
└── .env.example
```

### Main App

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import items
from src.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Config con Pydantic

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My API"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### Router Pattern

```python
# src/api/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from src.services.item_service import ItemService
from src.dependencies import get_item_service

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    service: ItemService = Depends(get_item_service)
):
    return await service.get_all(skip=skip, limit=limit)

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    item = await service.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service)
):
    return await service.create(item)

@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    item: ItemUpdate,
    service: ItemService = Depends(get_item_service)
):
    updated = await service.update(item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    service: ItemService = Depends(get_item_service)
):
    deleted = await service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
```

### Schemas con Pydantic

```python
# src/schemas/item.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float | None = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None

class ItemResponse(ItemBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

---

## React 19 Patterns

### Server Components (default)

```tsx
// app/dashboard/page.tsx
import { createClient } from '@/lib/supabase/server'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: items } = await supabase.from('items').select('*')

  return (
    <div>
      <h1>Dashboard</h1>
      <ItemList items={items ?? []} />
    </div>
  )
}
```

### Client Components (interactivos)

```tsx
// components/item-form.tsx
'use client'

import { useActionState } from 'react'
import { createItem } from '@/app/actions/items'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export function ItemForm() {
  const [state, action, pending] = useActionState(createItem, null)

  return (
    <form action={action} className="space-y-4">
      <Input name="name" placeholder="Item name" required />
      <Input name="description" placeholder="Description" />
      
      {state?.error && (
        <p className="text-sm text-destructive">{state.error}</p>
      )}
      
      <Button type="submit" disabled={pending}>
        {pending ? 'Creating...' : 'Create Item'}
      </Button>
    </form>
  )
}
```

### Server Actions

```typescript
// app/actions/items.ts
'use server'

import { revalidatePath } from 'next/cache'
import { createClient } from '@/lib/supabase/server'

export async function createItem(prevState: any, formData: FormData) {
  const supabase = await createClient()

  const { error } = await supabase.from('items').insert({
    name: formData.get('name') as string,
    description: formData.get('description') as string,
  })

  if (error) {
    return { error: error.message }
  }

  revalidatePath('/dashboard')
  return { success: true }
}
```

### Estado Global (Zustand)

```typescript
// stores/use-app-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  theme: 'light' | 'dark'
  sidebarOpen: boolean
  setTheme: (theme: 'light' | 'dark') => void
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: 'light',
      sidebarOpen: true,
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    }),
    { name: 'app-storage' }
  )
)
```

---

## Styling (Tailwind 4 + shadcn)

### Setup shadcn

```bash
bunx shadcn@latest init
bunx shadcn@latest add button card input form table dialog
```

### Componente con Variantes (CVA)

```tsx
// components/ui/status-badge.tsx
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground',
        success: 'bg-green-100 text-green-800',
        warning: 'bg-yellow-100 text-yellow-800',
        error: 'bg-red-100 text-red-800',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

interface StatusBadgeProps extends VariantProps<typeof badgeVariants> {
  children: React.ReactNode
  className?: string
}

export function StatusBadge({ variant, className, children }: StatusBadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)}>
      {children}
    </span>
  )
}
```

### Layout Responsive

```tsx
// components/layout/dashboard-layout.tsx
export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar - hidden on mobile */}
      <aside className="fixed inset-y-0 left-0 z-50 hidden w-64 border-r bg-card md:block">
        <Sidebar />
      </aside>

      {/* Main content */}
      <main className="md:pl-64">
        <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur">
          <Navbar />
        </header>
        <div className="container py-6">
          {children}
        </div>
      </main>
    </div>
  )
}
```

---

## Base de Datos (Supabase)

### Row Level Security

```sql
-- Enable RLS
ALTER TABLE items ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own items
CREATE POLICY "Users can view own items"
ON items FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can insert their own items
CREATE POLICY "Users can insert own items"
ON items FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own items
CREATE POLICY "Users can update own items"
ON items FOR UPDATE
USING (auth.uid() = user_id);

-- Policy: Users can delete their own items
CREATE POLICY "Users can delete own items"
ON items FOR DELETE
USING (auth.uid() = user_id);
```

### Queries Comunes

```typescript
// Fetch con filtros
const { data } = await supabase
  .from('items')
  .select('*, category:categories(name)')
  .eq('status', 'active')
  .order('created_at', { ascending: false })
  .range(0, 9) // Pagination

// Upsert
const { data } = await supabase
  .from('items')
  .upsert({ id: itemId, ...updates })
  .select()
  .single()

// Count
const { count } = await supabase
  .from('items')
  .select('*', { count: 'exact', head: true })
  .eq('status', 'active')
```

### Realtime Subscriptions

```typescript
// hooks/use-realtime-items.ts
'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

export function useRealtimeItems(initialItems: Item[]) {
  const [items, setItems] = useState(initialItems)
  const supabase = createClient()

  useEffect(() => {
    const channel = supabase
      .channel('items-changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'items' },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setItems((prev) => [payload.new as Item, ...prev])
          } else if (payload.eventType === 'UPDATE') {
            setItems((prev) =>
              prev.map((item) =>
                item.id === payload.new.id ? (payload.new as Item) : item
              )
            )
          } else if (payload.eventType === 'DELETE') {
            setItems((prev) =>
              prev.filter((item) => item.id !== payload.old.id)
            )
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [supabase])

  return items
}
```

---

## MVP Checklist

### Mínimo Viable

- [ ] **Auth**: Login/Signup con Supabase
- [ ] **CRUD**: Operaciones básicas de la entidad principal
- [ ] **UI**: Layout responsive con shadcn
- [ ] **Deploy**: Vercel (frontend) + Supabase (backend)

### Nice to Have

- [ ] **Realtime**: Subscriptions para updates en vivo
- [ ] **Search**: Filtros y búsqueda
- [ ] **Pagination**: Infinite scroll o páginas
- [ ] **Dark mode**: Theme toggle

### Pre-Launch

- [ ] **Error handling**: Toast notifications
- [ ] **Loading states**: Skeletons/spinners
- [ ] **SEO**: Meta tags, OG images
- [ ] **Analytics**: Vercel Analytics o Plausible

---

## Comandos de Scaffold

### Nuevo Proyecto Next.js + shadcn

```bash
bun create next-app@latest my-app --typescript --tailwind --eslint --app --src-dir
cd my-app
bunx shadcn@latest init -d
bunx shadcn@latest add button card input form table dialog dropdown-menu
```

### Nuevo Backend FastAPI

```bash
mkdir backend && cd backend
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pydantic-settings python-dotenv
mkdir -p src/{api,models,schemas,services}
touch src/__init__.py src/main.py src/config.py
```

### Supabase Local

```bash
supabase init
supabase start
# Dashboard: http://localhost:54323
```
