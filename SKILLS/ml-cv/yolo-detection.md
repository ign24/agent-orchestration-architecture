# Skill: YOLO Detection Setup

## Trigger
- "detectar objetos", "object detection", "YOLO"
- "ultralytics", "deteccion en imagenes/video"

## Context7
Para documentacion actualizada:
- `/ultralytics/ultralytics` - YOLO26 APIs, training, inference
- `/roboflow/supervision` - Anotaciones, tracking, utilities

Agregar `use context7` cuando necesites ejemplos actualizados.

---

## Pre-requisitos
- [ ] Python 3.11+ con GPU support (opcional pero recomendado)
- [ ] Proyecto ML existente o crear nuevo
- [ ] Imágenes/video para testear

---

## Steps

### 1. Instalar dependencias
```bash
pip install ultralytics supervision
```

### 2. Verificar instalación
```python
from ultralytics import YOLO
import supervision as sv

print(f"Ultralytics: {ultralytics.__version__}")
print(f"Supervision: {sv.__version__}")
```

### 3. Inferencia básica con YOLO
```python
from ultralytics import YOLO

# Cargar modelo pre-entrenado
model = YOLO("yolo26n.pt")  # nano - mas rapido
# model = YOLO("yolo26s.pt")  # small
# model = YOLO("yolo26m.pt")  # medium
# model = YOLO("yolo26l.pt")  # large
# model = YOLO("yolo26x.pt")  # extra large

# Inferencia en imagen
results = model("path/to/image.jpg")

# Procesar resultados
for result in results:
    boxes = result.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        class_name = model.names[cls]
        print(f"{class_name}: {conf:.2f} at {xyxy}")
```

### 4. Inferencia en video
```python
from ultralytics import YOLO

model = YOLO("yolo26n.pt")

# Procesar video
results = model("path/to/video.mp4", stream=True)

for result in results:
    # Cada frame
    annotated = result.plot()  # Frame con anotaciones
    # cv2.imshow("Detection", annotated)
```

### 5. Visualización con Supervision
```python
import cv2
import supervision as sv
from ultralytics import YOLO

model = YOLO("yolo26n.pt")

# Cargar imagen
image = cv2.imread("path/to/image.jpg")

# Inferencia
results = model(image)[0]

# Convertir a formato Supervision
detections = sv.Detections.from_ultralytics(results)

# Anotar
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

labels = [
    f"{model.names[class_id]} {confidence:.2f}"
    for class_id, confidence in zip(detections.class_id, detections.confidence)
]

annotated = box_annotator.annotate(scene=image.copy(), detections=detections)
annotated = label_annotator.annotate(scene=annotated, detections=detections, labels=labels)

cv2.imwrite("output.jpg", annotated)
```

### 6. Tracking de objetos
```python
import supervision as sv
from ultralytics import YOLO

model = YOLO("yolo26n.pt")
tracker = sv.ByteTrack()

cap = cv2.VideoCapture("video.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    
    # Tracking
    detections = tracker.update_with_detections(detections)
    
    # Anotar con IDs
    labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]
    # ...

cap.release()
```

### 7. Script de inferencia reutilizable
```python
# scripts/detect.py
import argparse
from pathlib import Path

import cv2
import supervision as sv
from ultralytics import YOLO


def detect(
    source: str,
    model_path: str = "yolo26n.pt",
    conf_threshold: float = 0.25,
    output_dir: str = "outputs/detections",
):
    """Run detection on image or video."""
    model = YOLO(model_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Annotators
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    
    results = model(source, conf=conf_threshold, stream=True)
    
    for i, result in enumerate(results):
        detections = sv.Detections.from_ultralytics(result)
        
        labels = [
            f"{model.names[class_id]} {conf:.2f}"
            for class_id, conf in zip(detections.class_id, detections.confidence)
        ]
        
        frame = result.orig_img.copy()
        frame = box_annotator.annotate(scene=frame, detections=detections)
        frame = label_annotator.annotate(scene=frame, detections=detections, labels=labels)
        
        # Guardar
        output_file = output_path / f"detection_{i:04d}.jpg"
        cv2.imwrite(str(output_file), frame)
        print(f"Saved: {output_file}")
    
    print(f"Done! Results in {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Image or video path")
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--output", default="outputs/detections")
    args = parser.parse_args()
    
    detect(args.source, args.model, args.conf, args.output)
```

---

## Modelos Disponibles (YOLO26 - 2026)

| Modelo | Parametros | mAP | Velocidad |
|--------|------------|-----|-----------|
| yolo26n | 2.6M | 39.5 | Muy rapido |
| yolo26s | 9.4M | 47.0 | Rapido |
| yolo26m | 20.1M | 51.5 | Medio |
| yolo26l | 25.3M | 53.4 | Lento |
| yolo26x | 56.9M | 54.7 | Muy lento |

**Variantes:**
- `yolo26n.pt` - Detection
- `yolo26n-seg.pt` - Instance Segmentation
- `yolo26n-cls.pt` - Classification
- `yolo26n-pose.pt` - Pose Estimation
- `yolo26n-obb.pt` - Oriented Bounding Boxes

---

## Verification
- [ ] Modelo carga sin errores
- [ ] Detecciones retornan en imagen de prueba
- [ ] Visualización con Supervision funciona
- [ ] Script de CLI corre correctamente

---

## Output
```
outputs/
└── detections/
    ├── detection_0000.jpg
    ├── detection_0001.jpg
    └── ...
```

---

## Autonomy: delegado

Ejecutar automáticamente:
- Instalación de dependencias
- Código de inferencia básico
- Script de detección

Preguntar antes de:
- Elegir tamaño de modelo (si no especificado)
- Procesar datasets grandes
