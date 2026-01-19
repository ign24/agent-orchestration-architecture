# Skill: Dataset Preparation (CV)

## Trigger
- "preparar dataset", "dataset para YOLO"
- "convertir anotaciones", "split train/val"

## Context7
Para documentación actualizada:
- `/ultralytics/ultralytics` - Dataset format requirements
- `/roboflow/supervision` - Dataset utilities

Agregar `use context7` cuando necesites ejemplos actualizados.

---

## Pre-requisitos
- [ ] Imágenes disponibles
- [ ] Anotaciones (COCO, Pascal VOC, o Roboflow export)
- [ ] Lista de clases definida

---

## Steps

### 1. Estructura objetivo (YOLO format)
```
dataset/
├── train/
│   ├── images/
│   │   ├── img001.jpg
│   │   └── ...
│   └── labels/
│       ├── img001.txt
│       └── ...
├── val/
│   ├── images/
│   └── labels/
├── test/  # opcional
│   ├── images/
│   └── labels/
└── data.yaml
```

### 2. Formato de labels YOLO
```
# Cada línea: class_id x_center y_center width height
# Valores normalizados (0-1)

0 0.5 0.5 0.2 0.3
1 0.3 0.7 0.1 0.15
```

### 3. Script de conversión desde COCO
```python
# scripts/convert_coco_to_yolo.py
import json
from pathlib import Path


def convert_coco_to_yolo(
    coco_json: str,
    images_dir: str,
    output_dir: str,
):
    """Convert COCO annotations to YOLO format."""
    with open(coco_json) as f:
        coco = json.load(f)
    
    output_path = Path(output_dir)
    (output_path / "images").mkdir(parents=True, exist_ok=True)
    (output_path / "labels").mkdir(parents=True, exist_ok=True)
    
    # Mapeo de categorías
    cat_id_to_idx = {cat["id"]: i for i, cat in enumerate(coco["categories"])}
    class_names = [cat["name"] for cat in coco["categories"]]
    
    # Mapeo de imágenes
    img_id_to_info = {img["id"]: img for img in coco["images"]}
    
    # Agrupar anotaciones por imagen
    img_annotations = {}
    for ann in coco["annotations"]:
        img_id = ann["image_id"]
        if img_id not in img_annotations:
            img_annotations[img_id] = []
        img_annotations[img_id].append(ann)
    
    # Convertir
    for img_id, img_info in img_id_to_info.items():
        img_name = img_info["file_name"]
        img_w = img_info["width"]
        img_h = img_info["height"]
        
        # Copiar imagen
        src_img = Path(images_dir) / img_name
        if src_img.exists():
            import shutil
            shutil.copy(src_img, output_path / "images" / img_name)
        
        # Crear label
        label_name = Path(img_name).stem + ".txt"
        label_path = output_path / "labels" / label_name
        
        annotations = img_annotations.get(img_id, [])
        lines = []
        
        for ann in annotations:
            cat_idx = cat_id_to_idx[ann["category_id"]]
            bbox = ann["bbox"]  # [x, y, width, height] en COCO
            
            # Convertir a YOLO format (center, normalized)
            x_center = (bbox[0] + bbox[2] / 2) / img_w
            y_center = (bbox[1] + bbox[3] / 2) / img_h
            width = bbox[2] / img_w
            height = bbox[3] / img_h
            
            lines.append(f"{cat_idx} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
        
        with open(label_path, "w") as f:
            f.write("\n".join(lines))
    
    print(f"Converted {len(img_id_to_info)} images to YOLO format")
    print(f"Classes: {class_names}")
    
    return class_names


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--coco", required=True, help="Path to COCO JSON")
    parser.add_argument("--images", required=True, help="Path to images directory")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()
    
    convert_coco_to_yolo(args.coco, args.images, args.output)
```

### 4. Script de split train/val
```python
# scripts/split_dataset.py
import random
import shutil
from pathlib import Path


def split_dataset(
    source_dir: str,
    output_dir: str,
    val_ratio: float = 0.2,
    test_ratio: float = 0.0,
    seed: int = 42,
):
    """Split dataset into train/val/test."""
    random.seed(seed)
    
    source = Path(source_dir)
    output = Path(output_dir)
    
    # Obtener todas las imágenes
    images = list((source / "images").glob("*"))
    random.shuffle(images)
    
    # Calcular splits
    n_total = len(images)
    n_val = int(n_total * val_ratio)
    n_test = int(n_total * test_ratio)
    n_train = n_total - n_val - n_test
    
    splits = {
        "train": images[:n_train],
        "val": images[n_train:n_train + n_val],
    }
    if test_ratio > 0:
        splits["test"] = images[n_train + n_val:]
    
    # Copiar archivos
    for split_name, split_images in splits.items():
        img_dir = output / split_name / "images"
        lbl_dir = output / split_name / "labels"
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        
        for img_path in split_images:
            # Copiar imagen
            shutil.copy(img_path, img_dir / img_path.name)
            
            # Copiar label
            label_name = img_path.stem + ".txt"
            label_path = source / "labels" / label_name
            if label_path.exists():
                shutil.copy(label_path, lbl_dir / label_name)
        
        print(f"{split_name}: {len(split_images)} images")
    
    print(f"\nDataset split complete: {output}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Source directory with images/ and labels/")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--test-ratio", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    
    split_dataset(args.source, args.output, args.val_ratio, args.test_ratio, args.seed)
```

### 5. Crear data.yaml
```python
# scripts/create_data_yaml.py
from pathlib import Path
import yaml


def create_data_yaml(
    dataset_dir: str,
    class_names: list[str],
    output_path: str = None,
):
    """Create data.yaml for YOLO training."""
    dataset_path = Path(dataset_dir).resolve()
    
    data = {
        "path": str(dataset_path),
        "train": "train/images",
        "val": "val/images",
        "nc": len(class_names),
        "names": class_names,
    }
    
    # Check if test exists
    if (dataset_path / "test" / "images").exists():
        data["test"] = "test/images"
    
    output = output_path or dataset_path / "data.yaml"
    with open(output, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print(f"Created: {output}")
    print(yaml.dump(data, default_flow_style=False))
    
    return str(output)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Dataset directory")
    parser.add_argument("--classes", nargs="+", required=True, help="Class names")
    args = parser.parse_args()
    
    create_data_yaml(args.dataset, args.classes)
```

### 6. Validar dataset
```python
# scripts/validate_dataset.py
from pathlib import Path


def validate_dataset(dataset_dir: str):
    """Validate YOLO dataset structure."""
    dataset = Path(dataset_dir)
    issues = []
    
    # Check structure
    for split in ["train", "val"]:
        img_dir = dataset / split / "images"
        lbl_dir = dataset / split / "labels"
        
        if not img_dir.exists():
            issues.append(f"Missing: {img_dir}")
            continue
        
        if not lbl_dir.exists():
            issues.append(f"Missing: {lbl_dir}")
            continue
        
        # Check matching
        images = set(p.stem for p in img_dir.glob("*"))
        labels = set(p.stem for p in lbl_dir.glob("*.txt"))
        
        missing_labels = images - labels
        if missing_labels:
            issues.append(f"{split}: {len(missing_labels)} images without labels")
        
        extra_labels = labels - images
        if extra_labels:
            issues.append(f"{split}: {len(extra_labels)} labels without images")
        
        print(f"{split}: {len(images)} images, {len(labels)} labels")
    
    # Check data.yaml
    data_yaml = dataset / "data.yaml"
    if not data_yaml.exists():
        issues.append("Missing: data.yaml")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\nDataset validation: PASSED")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help="Dataset directory")
    args = parser.parse_args()
    
    validate_dataset(args.dataset)
```

---

## Comandos Rápidos

```bash
# Convertir COCO a YOLO
python scripts/convert_coco_to_yolo.py --coco annotations.json --images images/ --output converted/

# Split dataset
python scripts/split_dataset.py --source converted/ --output dataset/ --val-ratio 0.2

# Crear data.yaml
python scripts/create_data_yaml.py --dataset dataset/ --classes person car bike

# Validar
python scripts/validate_dataset.py dataset/
```

---

## Verification
- [ ] Estructura de carpetas correcta
- [ ] Labels en formato YOLO (class x_center y_center w h)
- [ ] data.yaml creado con paths correctos
- [ ] Validación pasa sin errores

---

## Output
```
dataset/
├── train/
│   ├── images/ (N imágenes)
│   └── labels/ (N labels)
├── val/
│   ├── images/ (M imágenes)
│   └── labels/ (M labels)
└── data.yaml
```

---

## Autonomy: co-pilot

Ejecutar automáticamente:
- Conversión de formatos
- Split de dataset
- Validación

Pedir confirmación antes de:
- Borrar archivos originales
- Ratio de split (usar default 80/20 si no especificado)
- Nombres de clases (si no están claros)
