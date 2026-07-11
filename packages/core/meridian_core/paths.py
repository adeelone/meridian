from __future__ import annotations

import os
from pathlib import Path


def data_path(filename: str) -> Path:
    default_root = Path(os.getenv("LOCALAPPDATA", ".")) / "Meridian"
    return Path(os.getenv("MERIDIAN_HOME", str(default_root))) / filename
