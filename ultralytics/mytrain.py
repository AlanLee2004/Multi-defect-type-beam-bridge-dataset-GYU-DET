from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_CONFIG = Path(__file__).with_name("GZ-DET.yaml")
DEFAULT_MODEL = "yolo26m.pt"


def parse_args():
    parser = argparse.ArgumentParser(description="Train GYU-DET with YOLO26m by default.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model weights to train from.")
    parser.add_argument("--data", default=str(DATASET_CONFIG), help="Dataset YAML path.")
    parser.add_argument("--epochs", type=int, default=300, help="Training epochs.")
    return parser.parse_args()


def get_yolo_cls():
    project_root = str(PROJECT_ROOT)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from ultralytics import YOLO

    return YOLO


if __name__ == "__main__":
    args = parse_args()
    YOLO = get_yolo_cls()
    model = YOLO(args.model)
    model.train(data=args.data, epochs=args.epochs)
