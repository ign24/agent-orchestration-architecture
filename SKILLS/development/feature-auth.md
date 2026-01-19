# Skill: Feature Auth (Supabase)

## Trigger
- "agregar autenticación", "login/signup", "auth"
- "proteger rutas", "usuarios"

## Context7
Para documentación actualizada:
- `/supabase/supabase` - Auth, RLS, client setup
- `/vercel/next.js` - Middleware, Server Actions

Agregar `use context7` cuando necesites ejemplos actualizados.

---

## Pre-requisitos
- [ ] Proyecto Next.js existente
- [ ] Cuenta de Supabase (https://supabase.com)
- [ ] Proyecto Supabase creado con URL y anon key

---

## Steps

### 1. Instalar dependencias
```bash
bun add @supabase/supabase-js @supabase/ssr
```

### 2. Configurar variables de entorno
```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://[project-id].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon-key]
```

### 3. Crear cliente browser (lib/supabase/client.ts)
```typescript
import { createBrowserClient } from "@supabase/ssr";

export const createClient = () =>
  createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
```

### 4. Crear cliente server (lib/supabase/server.ts)
```typescript
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export const createClient = async () => {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Server Component - ignore
          }
        },
      },
    }
  );
};
```

### 5. Crear middleware (middleware.ts)
```typescript
import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  // Rutas protegidas
  if (!user && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Redirigir usuarios logueados fuera de login
  if (user && request.nextUrl.pathname === "/login") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return response;
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|api/webhook).*)",
  ],
};
```

### 6. Crear Server Actions (app/actions/auth.ts)
```typescript
"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export async function signIn(formData: FormData) {
  const supabase = await createClient();

  const { error } = await supabase.auth.signInWithPassword({
    email: formData.get("email") as string,
    password: formData.get("password") as string,
  });

  if (error) {
    return { error: error.message };
  }

  revalidatePath("/", "layout");
  redirect("/dashboard");
}

export async function signUp(formData: FormData) {
  const supabase = await createClient();

  const { error } = await supabase.auth.signUp({
    email: formData.get("email") as string,
    password: formData.get("password") as string,
  });

  if (error) {
    return { error: error.message };
  }

  revalidatePath("/", "layout");
  redirect("/verify-email");
}

export async function signOut() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/login");
}
```

### 7. Crear página de login (app/login/page.tsx)
```tsx
"use client";

import { useActionState } from "react";
import { signIn, signUp } from "@/app/actions/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function LoginPage() {
  const [signInState, signInAction, signInPending] = useActionState(signIn, null);
  const [signUpState, signUpAction, signUpPending] = useActionState(signUp, null);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Iniciar Sesión</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form action={signInAction} className="space-y-4">
            <Input name="email" type="email" placeholder="Email" required />
            <Input name="password" type="password" placeholder="Contraseña" required />
            
            {signInState?.error && (
              <p className="text-sm text-destructive">{signInState.error}</p>
            )}
            
            <Button type="submit" className="w-full" disabled={signInPending}>
              {signInPending ? "Ingresando..." : "Ingresar"}
            </Button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                O registrate
              </span>
            </div>
          </div>

          <form action={signUpAction} className="space-y-4">
            <Input name="email" type="email" placeholder="Email" required />
            <Input name="password" type="password" placeholder="Contraseña" required />
            
            {signUpState?.error && (
              <p className="text-sm text-destructive">{signUpState.error}</p>
            )}
            
            <Button type="submit" variant="outline" className="w-full" disabled={signUpPending}>
              {signUpPending ? "Registrando..." : "Crear cuenta"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
```

### 8. Crear página de verificación (app/verify-email/page.tsx)
```tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>Verificá tu email</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Te enviamos un link de verificación. Revisá tu bandeja de entrada.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
```

### 9. Helper para obtener usuario en Server Components
```typescript
// lib/supabase/get-user.ts
import { createClient } from "@/lib/supabase/server";

export async function getUser() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  return user;
}
```

### 10. Ejemplo de uso en dashboard
```tsx
// app/dashboard/page.tsx
import { getUser } from "@/lib/supabase/get-user";
import { signOut } from "@/app/actions/auth";
import { Button } from "@/components/ui/button";

export default async function DashboardPage() {
  const user = await getUser();

  return (
    <div className="container py-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">{user?.email}</span>
          <form action={signOut}>
            <Button variant="outline" size="sm">
              Cerrar sesión
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
```

---

## Verification
- [ ] Login funciona con email/password
- [ ] Signup crea usuario y envía verificación
- [ ] Middleware redirige correctamente
- [ ] Dashboard muestra email del usuario
- [ ] Logout funciona

---

## Archivos Creados/Modificados
```
src/
├── lib/supabase/
│   ├── client.ts
│   ├── server.ts
│   └── get-user.ts
├── app/
│   ├── actions/auth.ts
│   ├── login/page.tsx
│   ├── verify-email/page.tsx
│   └── dashboard/page.tsx
└── middleware.ts
```

---

## Autonomy: co-pilot

Pedir confirmación antes de:
- Crear/modificar middleware.ts
- Definir rutas protegidas
- Modificar páginas existentes

Ejecutar sin confirmación:
- Crear archivos en lib/supabase/
- Crear Server Actions
- Crear páginas nuevas (login, verify-email)
