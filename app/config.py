from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = ROOT_DIR / "uploads"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)