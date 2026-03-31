"""Wrapper de compatibilidad para la CLI de bodega por mediana libre."""

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from distance_routing.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["warehouse-median"]))
