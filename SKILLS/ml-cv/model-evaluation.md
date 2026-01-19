# Skill: Model Evaluation

## Trigger
- "evaluar modelo", "comparar con baseline"
- "métricas", "benchmark", "test model"

## Context7
Para documentación actualizada:
- `/ultralytics/ultralytics` - Validation API, metrics
- `/roboflow/supervision` - Evaluation utilities

Agregar `use context7` cuando necesites ejemplos actualizados.

---

## Pre-requisitos
- [ ] Modelo entrenado (.pt file)
- [ ] Dataset de validación/test
- [ ] Baseline metrics (para comparación)

---

## Steps

### 1. Evaluación básica con YOLO
```python
from ultralytics import YOLO

model = YOLO("path/to/best.pt")
metrics = model.val(data="data.yaml")

print(f"mAP50: {metrics.box.map50:.4f}")
print(f"mAP50-95: {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.mp:.4f}")
print(f"Recall: {metrics.box.mr:.4f}")
```

### 2. Evaluación completa con reporte
```python
# scripts/full_evaluation.py
import json
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


def full_evaluation(
    model_path: str,
    data_yaml: str,
    output_dir: str = "outputs/evaluation",
    baseline_path: str = None,
):
    """Run comprehensive model evaluation."""
    model = YOLO(model_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # === Validation metrics ===
    print("Running validation...")
    metrics = model.val(data=data_yaml, verbose=False)
    
    results = {
        "timestamp": timestamp,
        "model": model_path,
        "data": data_yaml,
        "overall": {
            "mAP50": float(metrics.box.map50),
            "mAP50-95": float(metrics.box.map),
            "precision": float(metrics.box.mp),
            "recall": float(metrics.box.mr),
            "fitness": float(metrics.fitness),
        },
        "per_class": {},
        "inference": {
            "speed_preprocess_ms": float(metrics.speed["preprocess"]),
            "speed_inference_ms": float(metrics.speed["inference"]),
            "speed_postprocess_ms": float(metrics.speed["postprocess"]),
        },
    }
    
    # Per-class metrics
    for i, name in enumerate(metrics.names.values()):
        results["per_class"][name] = {
            "AP50": float(metrics.box.ap50[i]),
            "AP50-95": float(metrics.box.ap[i]),
        }
    
    # === Baseline comparison ===
    if baseline_path and Path(baseline_path).exists():
        with open(baseline_path) as f:
            baseline = json.load(f)
        
        results["comparison"] = {
            "baseline_file": baseline_path,
            "improvement": {},
        }
        
        for metric in ["mAP50", "mAP50-95", "precision", "recall"]:
            curr = results["overall"][metric]
            base = baseline.get("overall", {}).get(metric, 0)
            diff = curr - base
            diff_pct = (diff / base * 100) if base > 0 else 0
            
            results["comparison"]["improvement"][metric] = {
                "current": curr,
                "baseline": base,
                "diff": diff,
                "diff_percent": diff_pct,
            }
    
    # === Save results ===
    results_file = output / f"evaluation_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # === Print summary ===
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Model: {model_path}")
    print(f"Data: {data_yaml}")
    print("-"*60)
    print(f"mAP50:     {results['overall']['mAP50']:.4f}")
    print(f"mAP50-95:  {results['overall']['mAP50-95']:.4f}")
    print(f"Precision: {results['overall']['precision']:.4f}")
    print(f"Recall:    {results['overall']['recall']:.4f}")
    print("-"*60)
    print(f"Inference: {results['inference']['speed_inference_ms']:.1f}ms")
    print("-"*60)
    
    if "comparison" in results:
        print("\nCOMPARISON vs BASELINE:")
        for metric, data in results["comparison"]["improvement"].items():
            sign = "+" if data["diff"] > 0 else ""
            print(f"  {metric}: {data['current']:.4f} ({sign}{data['diff_percent']:.1f}%)")
    
    print("="*60)
    print(f"Saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", default="outputs/evaluation")
    parser.add_argument("--baseline", default=None)
    args = parser.parse_args()
    
    full_evaluation(args.model, args.data, args.output, args.baseline)
```

### 3. Análisis de errores
```python
# scripts/error_analysis.py
import json
from pathlib import Path

import cv2
import supervision as sv
from ultralytics import YOLO


def analyze_errors(
    model_path: str,
    images_dir: str,
    labels_dir: str,
    output_dir: str = "outputs/errors",
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.5,
):
    """Analyze model errors: false positives, false negatives, misclassifications."""
    model = YOLO(model_path)
    output = Path(output_dir)
    
    (output / "false_positives").mkdir(parents=True, exist_ok=True)
    (output / "false_negatives").mkdir(parents=True, exist_ok=True)
    (output / "misclassifications").mkdir(parents=True, exist_ok=True)
    
    images_path = Path(images_dir)
    labels_path = Path(labels_dir)
    
    stats = {
        "total_images": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "misclassifications": 0,
        "correct": 0,
    }
    
    for img_file in images_path.glob("*"):
        if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue
        
        stats["total_images"] += 1
        
        # Load image
        image = cv2.imread(str(img_file))
        h, w = image.shape[:2]
        
        # Ground truth
        label_file = labels_path / (img_file.stem + ".txt")
        gt_boxes = []
        if label_file.exists():
            with open(label_file) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls, xc, yc, bw, bh = map(float, parts[:5])
                        x1 = (xc - bw/2) * w
                        y1 = (yc - bh/2) * h
                        x2 = (xc + bw/2) * w
                        y2 = (yc + bh/2) * h
                        gt_boxes.append((int(cls), x1, y1, x2, y2))
        
        # Predictions
        results = model(image, conf=conf_threshold, verbose=False)[0]
        pred_boxes = []
        for box in results.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            pred_boxes.append((cls, x1, y1, x2, y2, conf))
        
        # Simple matching (por IOU)
        matched_gt = set()
        matched_pred = set()
        
        for i, (p_cls, px1, py1, px2, py2, p_conf) in enumerate(pred_boxes):
            best_iou = 0
            best_gt = -1
            
            for j, (g_cls, gx1, gy1, gx2, gy2) in enumerate(gt_boxes):
                if j in matched_gt:
                    continue
                
                # Calcular IOU
                ix1 = max(px1, gx1)
                iy1 = max(py1, gy1)
                ix2 = min(px2, gx2)
                iy2 = min(py2, gy2)
                
                if ix2 > ix1 and iy2 > iy1:
                    inter = (ix2 - ix1) * (iy2 - iy1)
                    area1 = (px2 - px1) * (py2 - py1)
                    area2 = (gx2 - gx1) * (gy2 - gy1)
                    iou = inter / (area1 + area2 - inter)
                    
                    if iou > best_iou:
                        best_iou = iou
                        best_gt = j
            
            if best_iou >= iou_threshold and best_gt >= 0:
                matched_gt.add(best_gt)
                matched_pred.add(i)
                
                g_cls = gt_boxes[best_gt][0]
                if p_cls != g_cls:
                    stats["misclassifications"] += 1
                else:
                    stats["correct"] += 1
        
        # False positives: predicciones sin match
        fp_count = len(pred_boxes) - len(matched_pred)
        stats["false_positives"] += fp_count
        
        # False negatives: GT sin match
        fn_count = len(gt_boxes) - len(matched_gt)
        stats["false_negatives"] += fn_count
    
    # Save stats
    with open(output / "error_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    print("\nError Analysis:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Correct detections: {stats['correct']}")
    print(f"  False positives: {stats['false_positives']}")
    print(f"  False negatives: {stats['false_negatives']}")
    print(f"  Misclassifications: {stats['misclassifications']}")
    
    return stats
```

### 4. Benchmark de velocidad
```python
# scripts/benchmark_speed.py
import time
import torch
from ultralytics import YOLO


def benchmark_speed(
    model_path: str,
    imgsz: int = 640,
    warmup: int = 10,
    iterations: int = 100,
):
    """Benchmark model inference speed."""
    model = YOLO(model_path)
    
    # Dummy input
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dummy = torch.randn(1, 3, imgsz, imgsz).to(device)
    
    # Warmup
    print(f"Warmup ({warmup} iterations)...")
    for _ in range(warmup):
        model(dummy, verbose=False)
    
    # Benchmark
    print(f"Benchmarking ({iterations} iterations)...")
    torch.cuda.synchronize() if device == "cuda" else None
    
    start = time.perf_counter()
    for _ in range(iterations):
        model(dummy, verbose=False)
    torch.cuda.synchronize() if device == "cuda" else None
    end = time.perf_counter()
    
    total_time = end - start
    avg_time = total_time / iterations * 1000  # ms
    fps = iterations / total_time
    
    print(f"\nResults:")
    print(f"  Device: {device}")
    print(f"  Image size: {imgsz}x{imgsz}")
    print(f"  Average inference: {avg_time:.2f}ms")
    print(f"  FPS: {fps:.1f}")
    
    return {"device": device, "imgsz": imgsz, "avg_ms": avg_time, "fps": fps}
```

---

## Verification
- [ ] Métricas calculadas correctamente
- [ ] Comparación con baseline ejecutada
- [ ] Análisis de errores completado
- [ ] Resultados guardados en JSON

---

## Output
```
outputs/
└── evaluation/
    ├── evaluation_20260117_150000.json
    └── errors/
        ├── error_stats.json
        ├── false_positives/
        ├── false_negatives/
        └── misclassifications/
```

---

## Autonomy: delegado

Ejecutar automáticamente:
- Evaluación con métricas estándar
- Comparación con baseline
- Benchmark de velocidad

Reportar siempre:
- Resumen de métricas
- Comparación con baseline (si existe)
- Recomendación (actualizar baseline o no)
