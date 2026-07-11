from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4


def state_dir(name: str) -> Path:
    path = Path(os.getenv("TEMP", ".")) / "meridian-test-state" / f"{name}-{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path
