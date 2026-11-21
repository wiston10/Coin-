"""
Carga variables desde un archivo .env en la raíz del proyecto (sin dependencias externas).
Las variables ya definidas en el entorno tienen prioridad.
"""
import os
from pathlib import Path

_LOADED = False


def load_env(path: Path = None) -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    env_path = path or Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "si", "sí", "on")
