# Workflow: ML Experiment Cycle

## Objetivo
Ejecutar un ciclo completo de experimentación ML: desde hipótesis hasta resultados documentados.

## Pre-requisitos
- [ ] Hipótesis o pregunta a responder
- [ ] Dataset disponible (o fuente de datos)
- [ ] Baseline para comparar (modelo anterior o benchmark conocido)
- [ ] GPU disponible (recomendado)

---

## Flow Diagram

```
┌──────────────────────────┐
│ Fase 1: Definir          │
│ Hipótesis + Config       │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Fase 2: Data             │
│ Skill: dataset-prep      │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Fase 3: Training         │
│ Skill: training-pipeline │
└───────────┬──────────────┘
            │
            ▼
┌──────────────────────────┐
│ Fase 4: Evaluation       │
│ Skill: model-evaluation  │
└───────────┬──────────────┘
            │
            ▼
      ┌─────────────┐
      │ ¿Mejoró vs  │
      │ baseline?   │
      └──────┬──────┘
             │
        SÍ   │   NO
      ┌──────┴───────┐
      ▼              ▼
┌───────────┐  ┌───────────────┐
│ Guardar   │  │ Analizar      │
│ como      │  │ errores       │
│ nuevo     │  │               │
│ baseline  │  │ ¿Iterar?      │
└─────┬─────┘  └───────┬───────┘
      │                │
      │           SÍ   │   NO
      │         ┌──────┴──────┐
      │         │             │
      │         ▼             ▼
      │    [Volver a     ┌─────────┐
      │     Fase 1]      │ Cerrar  │
      │                  │ experim.│
      │                  └────┬────┘
      │                       │
      └───────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │ Fase 5: Log     │
        │ Documentar      │
        └─────────────────┘
```

---

## Fases

### Fase 1: Definir Experimento
**Duración:** 10-15 min

**Objetivo:** Establecer hipótesis clara y configuración

**Pasos:**
1. Definir hipótesis en formato testeable
2. Seleccionar modelo base
3. Definir métricas de éxito
4. Crear config de experimento

**Template de Hipótesis:**
```markdown
## Experimento: [nombre]

### Hipótesis
Si [cambio/acción], entonces [resultado esperado] porque [razón].

Ejemplo:
"Si aumento el tamaño del modelo de yolo11n a yolo11s, 
entonces mAP50 mejorará >5% porque el modelo tendrá 
más capacidad para features complejos."

### Baseline
- Modelo: [nombre]
- mAP50: [valor]
- mAP50-95: [valor]

### Métricas de Éxito
- mAP50 > [threshold]
- Latencia < [threshold]ms

### Config
- Model: [model]
- Epochs: [n]
- Batch: [n]
- LR: [value]
```

**Checkpoint:**
```
✓ Hipótesis definida
✓ Baseline establecido
✓ Config creada

¿Proceder con preparación de datos? [sí/modificar]
```

---

### Fase 2: Preparación de Datos
**Skill:** `dataset-prep`
**Duración:** 15-30 min (depende del tamaño)

**Objetivo:** Dataset listo para training

**Pasos:**
1. Verificar/convertir formato (YOLO)
2. Split train/val
3. Crear data.yaml
4. Validar estructura

**Checkpoint:**
```
Dataset preparado:
- Train: [N] imágenes
- Val: [M] imágenes
- Clases: [lista]

Validación: ✓ PASSED

¿Proceder con training? [sí/revisar datos]
```

---

### Fase 3: Training
**Skill:** `training-pipeline`
**Duración:** 30 min - varias horas

**Objetivo:** Entrenar modelo con config definida

**Pasos:**
1. Verificar GPU disponible
2. Iniciar training
3. Monitorear métricas
4. Guardar checkpoints

**Pre-checkpoint (antes de training largo):**
```
Training config:
- Model: [model]
- Epochs: [n]
- Batch: [n]
- Estimated time: [X hours]
- GPU: [name] ([memory]GB)

¿Iniciar training? [sí/modificar config]
```

**Checkpoint post-training:**
```
Training completado:
- Epochs: [n]
- Best mAP50: [value]
- Best epoch: [n]
- Time: [duration]

Weights saved: outputs/training/[run]/weights/best.pt

¿Proceder con evaluación? [sí]
```

---

### Fase 4: Evaluación
**Skill:** `model-evaluation`
**Duración:** 10-15 min

**Objetivo:** Evaluar modelo y comparar con baseline

**Pasos:**
1. Correr evaluación en val set
2. Calcular todas las métricas
3. Comparar con baseline
4. Análisis de errores (opcional)

**Checkpoint con decisión:**
```
RESULTADOS DEL EXPERIMENTO

Métricas:
| Metric     | Baseline | Current | Diff    |
|------------|----------|---------|---------|
| mAP50      | 0.850    | 0.872   | +2.6%   |
| mAP50-95   | 0.720    | 0.738   | +2.5%   |
| Precision  | 0.880    | 0.891   | +1.2%   |
| Recall     | 0.820    | 0.845   | +3.0%   |
| Latency    | 8.2ms    | 12.1ms  | +47.5%  |

Conclusión: MEJORADO (pero latencia aumentó)

Opciones:
1. Actualizar baseline con nuevo modelo
2. Iterar (probar otro approach)
3. Cerrar experimento (sin cambios)

¿Qué hacer? [1/2/3]
```

---

### Fase 5: Documentación
**Duración:** 5-10 min

**Objetivo:** Registrar resultados para referencia futura

**Pasos:**
1. Guardar métricas en experiment log
2. Actualizar PROJECT_CONTEXT.md
3. Actualizar baseline (si aplica)
4. Documentar learnings

**Template de Log:**
```markdown
## Experimento: [nombre]
Fecha: [fecha]

### Hipótesis
[hipótesis original]

### Resultado
[CONFIRMADA / RECHAZADA / PARCIAL]

### Métricas Finales
- mAP50: [value] (baseline: [value])
- mAP50-95: [value] (baseline: [value])

### Conclusiones
[Qué aprendimos]

### Próximos Pasos
[Si iteramos, qué probar]

### Artifacts
- Model: outputs/training/[run]/weights/best.pt
- Metrics: outputs/evaluation/[file].json
- Config: configs/[experiment].yaml
```

---

## Iteración

Si el experimento no mejora:

### Opciones de iteración:
1. **Más datos:** Agregar más imágenes de training
2. **Más epochs:** Entrenar más tiempo
3. **Hyperparams:** Ajustar LR, batch, augmentation
4. **Modelo más grande:** Probar yolo11s/m/l
5. **Data augmentation:** Más augmentation
6. **Limpiar datos:** Revisar labels problemáticos

### Volver a Fase 1 con:
```markdown
## Iteración 2

### Hipótesis anterior
[qué probamos]

### Por qué no funcionó
[análisis]

### Nueva hipótesis
[qué probar ahora]
```

---

## Estado a Persistir

Guardar en `PROJECT_CONTEXT.md`:

```markdown
## Experimento Activo: [nombre]
Estado: Fase [N] completada

### Hipótesis
[descripción]

### Baseline Actual
- Model: [path]
- mAP50: [value]
- Última actualización: [fecha]

### Historial de Iteraciones
1. [fecha]: [descripción] → [resultado]
2. [fecha]: [descripción] → [resultado]

### Próximo Paso
[qué hacer en la siguiente sesión]
```

---

## Estimación de Tiempo

| Fase | Tiempo |
|------|--------|
| Definir | 10-15 min |
| Data prep | 15-30 min |
| Training | 30 min - horas |
| Evaluation | 10-15 min |
| Documentation | 5-10 min |
| **Total** | **1-4+ horas** |

---

## Autonomy

**Fases como "delegado":**
- Data prep (si formato claro)
- Evaluation (métricas estándar)

**Fases como "co-pilot":**
- Definición (confirmar hipótesis)
- Training (confirmar antes de iniciar)
- Post-eval (decisión humana requerida)

**Checkpoints obligatorios:**
- Antes de iniciar training largo
- Después de evaluación (decisión de actualizar baseline)
