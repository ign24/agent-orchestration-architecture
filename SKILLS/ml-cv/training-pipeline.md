# Skill: ML Training Pipeline

## Trigger
- "entrenar modelo", "training", "fine-tune"
- "correr experimento", "train YOLO"

## Context7
Para documentación actualizada:
- `/ultralytics/ultralytics` - Training API, hyperparameters
- `/pytorch/pytorch` - DataLoader, optimizers

Agregar `use context7` cuando necesites ejemplos actualizados.

---

## Pre-requisitos
- [ ] Dataset preparado (ver skill: dataset-prep)
- [ ] Config de experimento definida
- [ ] Baseline para comparar (modelo anterior o conocido)
- [ ] GPU disponible (recomendado)

---

## Steps

### 1. Verificar estructura del dataset
```
dataset/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── data.yaml
```

### 2. Crear/verificar data.yaml
```yaml
# data.yaml
path: /path/to/dataset
train: train/images
val: val/images

nc: 3  # número de clases
names: ['class1', 'class2', 'class3']
```

### 3. Crear config de experimento
```yaml
# configs/experiment.yaml
model: yolo26n.pt
data: /path/to/data.yaml
epochs: 100
imgsz: 640
batch: 16
patience: 20
device: 0  # GPU index, o 'cpu'

# Hyperparameters
lr0: 0.01
lrf: 0.01
momentum: 0.937
weight_decay: 0.0005

# Augmentation
hsv_h: 0.015
hsv_s: 0.7
hsv_v: 0.4
degrees: 0.0
translate: 0.1
scale: 0.5
fliplr: 0.5
mosaic: 1.0
```

### 4. Script de training
```python
# scripts/train.py
import argparse
from datetime import datetime
from pathlib import Path

import yaml
from ultralytics import YOLO


def train(config_path: str):
    """Run training from config file."""
    # Cargar config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Timestamp para run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{Path(config['model']).stem}_{timestamp}"
    
    # Cargar modelo
    model = YOLO(config["model"])
    
    # Training
    results = model.train(
        data=config["data"],
        epochs=config["epochs"],
        imgsz=config["imgsz"],
        batch=config["batch"],
        patience=config.get("patience", 50),
        device=config.get("device", 0),
        project="outputs/training",
        name=run_name,
        # Hyperparams
        lr0=config.get("lr0", 0.01),
        lrf=config.get("lrf", 0.01),
        momentum=config.get("momentum", 0.937),
        weight_decay=config.get("weight_decay", 0.0005),
        # Augmentation
        hsv_h=config.get("hsv_h", 0.015),
        hsv_s=config.get("hsv_s", 0.7),
        hsv_v=config.get("hsv_v", 0.4),
        degrees=config.get("degrees", 0.0),
        translate=config.get("translate", 0.1),
        scale=config.get("scale", 0.5),
        fliplr=config.get("fliplr", 0.5),
        mosaic=config.get("mosaic", 1.0),
    )
    
    print(f"\nTraining complete!")
    print(f"Results saved to: outputs/training/{run_name}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config YAML")
    args = parser.parse_args()
    
    train(args.config)
```

### 5. Script de evaluación
```python
# scripts/evaluate.py
import argparse
import json
from pathlib import Path

from ultralytics import YOLO


def evaluate(model_path: str, data_path: str, output_dir: str = "outputs/evaluation"):
    """Evaluate model on validation set."""
    model = YOLO(model_path)
    
    # Validación
    metrics = model.val(data=data_path)
    
    # Extraer métricas
    results = {
        "model": model_path,
        "mAP50": float(metrics.box.map50),
        "mAP50-95": float(metrics.box.map),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "fitness": float(metrics.fitness),
    }
    
    # Per-class metrics
    results["per_class"] = {}
    for i, name in enumerate(metrics.names.values()):
        results["per_class"][name] = {
            "AP50": float(metrics.box.ap50[i]),
            "AP50-95": float(metrics.box.ap[i]),
        }
    
    # Guardar
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    output_file = output_path / "metrics.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation Results:")
    print(f"  mAP50: {results['mAP50']:.4f}")
    print(f"  mAP50-95: {results['mAP50-95']:.4f}")
    print(f"  Precision: {results['precision']:.4f}")
    print(f"  Recall: {results['recall']:.4f}")
    print(f"\nSaved to: {output_file}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to model weights")
    parser.add_argument("--data", required=True, help="Path to data.yaml")
    parser.add_argument("--output", default="outputs/evaluation")
    args = parser.parse_args()
    
    evaluate(args.model, args.data, args.output)
```

### 6. Comparación con baseline
```python
# scripts/compare_baseline.py
import json
from pathlib import Path


def compare(current_metrics: str, baseline_metrics: str):
    """Compare current model with baseline."""
    with open(current_metrics) as f:
        current = json.load(f)
    
    with open(baseline_metrics) as f:
        baseline = json.load(f)
    
    print("\n" + "="*50)
    print("COMPARISON: Current vs Baseline")
    print("="*50)
    
    metrics_to_compare = ["mAP50", "mAP50-95", "precision", "recall"]
    
    improved = True
    for metric in metrics_to_compare:
        curr_val = current.get(metric, 0)
        base_val = baseline.get(metric, 0)
        diff = curr_val - base_val
        diff_pct = (diff / base_val * 100) if base_val > 0 else 0
        
        status = "+" if diff > 0 else ""
        symbol = "^" if diff > 0 else "v" if diff < 0 else "="
        
        print(f"  {metric:12}: {curr_val:.4f} vs {base_val:.4f} ({status}{diff_pct:.1f}%) {symbol}")
        
        if metric == "mAP50-95" and diff < -0.01:  # 1% degradation threshold
            improved = False
    
    print("="*50)
    if improved:
        print("Result: IMPROVED - Consider updating baseline")
    else:
        print("Result: DEGRADED - Review changes")
    
    return improved
```

### 7. Logging de experimento
```python
# Al final del training, guardar contexto
experiment_log = {
    "timestamp": timestamp,
    "config": config,
    "results": {
        "best_mAP50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
        "best_mAP50-95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
        "final_epoch": results.epoch,
    },
    "model_path": f"outputs/training/{run_name}/weights/best.pt",
    "notes": "",  # Agregar notas manualmente
}

with open(f"outputs/training/{run_name}/experiment_log.json", "w") as f:
    json.dump(experiment_log, f, indent=2)
```

---

## Comandos Rápidos

```bash
# Training
python scripts/train.py --config configs/experiment.yaml

# Evaluación
python scripts/evaluate.py --model outputs/training/latest/weights/best.pt --data data.yaml

# Comparación
python scripts/compare_baseline.py outputs/evaluation/metrics.json baseline/metrics.json
```

---

## Verification
- [ ] Training inicia sin errores
- [ ] Loss decrece durante training
- [ ] Métricas se guardan correctamente
- [ ] Modelo exportado funciona
- [ ] Comparación con baseline ejecutada

---

## Output
```
outputs/
├── training/
│   └── yolo26n_20260117_143000/
│       ├── weights/
│       │   ├── best.pt
│       │   └── last.pt
│       ├── results.csv
│       ├── confusion_matrix.png
│       └── experiment_log.json
└── evaluation/
    └── metrics.json
```

---

## Autonomy: co-pilot

Ejecutar automáticamente:
- Verificación de estructura
- Training con config provista

Pedir confirmación antes de:
- Iniciar training largo (>1hr estimado)
- Si GPU no disponible (training en CPU es muy lento)
- Si métricas son significativamente peores que baseline

Checkpoint humano:
- Después de training: mostrar resultados y preguntar si actualizar baseline
