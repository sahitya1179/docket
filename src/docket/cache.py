"""Disk cache for external API responses.

PROTOCOLS.md P4: every external call is cached on first fetch. This keeps the
dev loop fast, keeps us inside Nominatim's usage policy, and stops repeated
runs from burning AWS credits.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .config import settings


class DiskCache:
    """Content-addressed JSON cache. Keys are hashed, so URLs of any length work."""

    def __init__(self, namespace: str, root: Path | None = None) -> None:
        self.dir = (root or settings.cache_dir) / namespace
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
        return self.dir / f"{digest}.json"

    def get(self, key: str) -> Any | None:
        path = self._path(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))["value"]
        except (json.JSONDecodeError, KeyError):
            # A partial write from an interrupted run. Treat as a miss.
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: Any) -> None:
        payload = json.dumps({"key": key, "value": value}, ensure_ascii=False)
        # Write to a temp file first so an interrupted run can't leave a half-file.
        tmp = self._path(key).with_suffix(".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(self._path(key))

    def __len__(self) -> int:
        return len(list(self.dir.glob("*.json")))
