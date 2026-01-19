# Skill: Debugging Sistemático

## Trigger
- "bug", "error", "no funciona", "falla"
- "debugging", "investigar problema"

## Context7
Usar context7 con la librería relevante al error.

---

## Pre-requisitos
- [ ] Descripción del error o comportamiento inesperado
- [ ] Pasos para reproducir (idealmente)
- [ ] Logs o mensajes de error

---

## Metodología

### Fase 1: Recopilar Información

```markdown
## Bug Report

### Descripción
[Qué está pasando vs qué debería pasar]

### Pasos para Reproducir
1. 
2. 
3. 

### Error/Logs
```
[Pegar error aquí]
```

### Contexto
- Archivo: 
- Función: 
- Última modificación: 
```

### Comandos de Diagnóstico

**Python:**
```bash
# Ver traceback completo
python -c "import traceback; traceback.print_exc()"

# Verificar imports
python -c "import [modulo]; print([modulo].__version__)"

# Verificar dependencias
pip list | grep [paquete]
```

**Node/Bun:**
```bash
# Verificar versiones
node --version
bun --version

# Verificar dependencias
bun pm ls | grep [paquete]

# Build con verbose
bun run build --verbose
```

**Git:**
```bash
# Ver cambios recientes
git log --oneline -10

# Ver diff del archivo problemático
git diff HEAD~5 -- [archivo]

# Buscar cuándo se introdujo
git bisect start
git bisect bad HEAD
git bisect good [commit-bueno]
```

---

### Fase 2: Aislar el Problema

#### 2.1 Reducir Scope
```
1. ¿El error ocurre siempre o intermitentemente?
2. ¿En qué archivo/función específica?
3. ¿Con qué inputs específicos?
4. ¿Funcionaba antes? ¿Qué cambió?
```

#### 2.2 Reproducir Mínimamente
```python
# Crear test case mínimo
def test_bug_reproduction():
    # Setup mínimo
    ...
    # Acción que causa el bug
    result = funcion_problematica(input_problematico)
    # Assert que falla
    assert result == expected, f"Got {result}"
```

#### 2.3 Verificar Hipótesis
```
Hipótesis 1: [descripción]
  - Test: [cómo verificar]
  - Resultado: [confirmado/descartado]

Hipótesis 2: [descripción]
  - Test: [cómo verificar]
  - Resultado: [confirmado/descartado]
```

---

### Fase 3: Debugging Activo

#### Estrategias por Tipo de Error

**TypeError / AttributeError (Python):**
```python
# Agregar logging temporal
print(f"DEBUG: type(variable) = {type(variable)}")
print(f"DEBUG: dir(variable) = {dir(variable)}")
print(f"DEBUG: variable = {variable}")
```

**Import Error:**
```python
import sys
print(sys.path)  # Ver paths de búsqueda
print(sys.modules.keys())  # Ver módulos cargados
```

**Async/Await Issues:**
```python
import asyncio
# Verificar que estás en contexto async
print(f"Running in event loop: {asyncio.get_running_loop()}")
```

**React/Next.js Hydration:**
```tsx
// Agregar key única
<Component key={uniqueId} />

// Verificar client/server mismatch
useEffect(() => {
  console.log("Client-side only");
}, []);
```

**API/Network Errors:**
```bash
# Probar endpoint directamente
curl -v http://localhost:8000/api/endpoint

# Ver headers
curl -I http://localhost:8000/api/endpoint
```

---

### Fase 4: Implementar Fix

#### Checklist Pre-Fix
- [ ] Entiendo la causa raíz (no solo el síntoma)
- [ ] Tengo test case que reproduce el bug
- [ ] El fix no rompe otras cosas

#### Aplicar Fix
```bash
# Crear branch para el fix
git checkout -b fix/descripcion-breve

# Hacer cambios mínimos necesarios
# ...

# Verificar que el test pasa
pytest tests/test_bug.py -v

# Verificar que no rompimos nada
pytest -x
```

#### Checklist Post-Fix
- [ ] Bug original resuelto
- [ ] Tests pasan
- [ ] Lint pasa
- [ ] No hay regresiones

---

### Fase 5: Documentar

```markdown
## Fix Aplicado

### Causa Raíz
[Explicación de por qué ocurría el bug]

### Solución
[Qué se cambió y por qué]

### Archivos Modificados
- path/to/file.py: [descripción del cambio]

### Cómo Prevenir en el Futuro
[Si aplica]
```

---

## Errores Comunes por Stack

### Python/FastAPI
| Error | Causa Común | Fix |
|-------|-------------|-----|
| `ModuleNotFoundError` | Dependencia no instalada | `pip install [modulo]` |
| `422 Unprocessable Entity` | Validación Pydantic falló | Verificar tipos de request body |
| `CORS error` | Middleware no configurado | Agregar `CORSMiddleware` |

### Next.js/React
| Error | Causa Común | Fix |
|-------|-------------|-----|
| Hydration mismatch | Diferencia server/client | Usar `useEffect` o `dynamic` import |
| `Cannot read property of undefined` | Datos no cargados | Optional chaining `data?.field` |
| Build fails | Type errors | `bun run build` para ver errores |

### Ultralytics/CV
| Error | Causa Común | Fix |
|-------|-------------|-----|
| `CUDA out of memory` | Batch muy grande | Reducir batch size |
| `No labels found` | Paths incorrectos | Verificar data.yaml |
| Métricas en 0 | Dataset mal formateado | Validar con `validate_dataset.py` |

---

## Verification
- [ ] Bug reproducido con test case
- [ ] Causa raíz identificada
- [ ] Fix implementado y testeado
- [ ] No hay regresiones
- [ ] Documentación actualizada

---

## Autonomy: co-pilot

Ejecutar automáticamente:
- Comandos de diagnóstico (read-only)
- Búsqueda en código
- Crear test cases

Pedir confirmación antes de:
- Modificar archivos
- Aplicar el fix
- Commitear cambios
