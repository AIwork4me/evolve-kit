"""Memory Manager — ADD / UPDATE / DELETE lifecycle for agent memory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from evolve_kit.types import MemoryEntry, MemoryOp


class MemoryManager:
    """Manages agent memory with structured ADD/UPDATE/DELETE operations.

    Key principles:
    - Never accumulate contradictory information
    - UPDATE replaces (merges), doesn't duplicate
    - DELETE logs the reason for traceability
    - Automatic conflict detection

    Based on: Mem0, Memory-R1 (arXiv 2507.21046 Section 3.2.1)
    """

    def __init__(
        self,
        store_path: str | Path = "./evolve-data/memory.json",
        deletions_path: str | Path = "./evolve-data/deletions.jsonl",
    ):
        self._path = Path(store_path)
        self._del_path = Path(deletions_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, key: str, value: str, tags: Optional[list[str]] = None) -> MemoryEntry:
        """ADD new knowledge. Raises if key already exists — use update() instead."""
        data = self._load()
        if key in data:
            raise KeyError(
                f"Key '{key}' already exists. Use update() to change it, "
                f"or delete() + add() to replace with a new entry."
            )
        entry = MemoryEntry(
            key=key,
            value=value,
            operation=MemoryOp.ADD,
            tags=tags or [],
        )
        data[key] = entry.to_dict()
        self._save(data)
        return entry

    def update(self, key: str, value: str, tags: Optional[list[str]] = None) -> MemoryEntry:
        """UPDATE existing knowledge. Replaces the value (no duplication)."""
        data = self._load()
        if key not in data:
            raise KeyError(f"Key '{key}' does not exist. Use add() to create it.")
        old_value = data[key].get("value", "")
        old_tags = data[key].get("tags", [])
        entry = MemoryEntry(
            key=key,
            value=value,
            operation=MemoryOp.UPDATE,
            previous_value=old_value,
            tags=tags if tags is not None else old_tags,
        )
        data[key] = entry.to_dict()
        self._save(data)
        return entry

    def upsert(self, key: str, value: str, tags: Optional[list[str]] = None) -> MemoryEntry:
        """ADD or UPDATE — safe operation that doesn't raise on duplicate keys."""
        data = self._load()
        if key in data:
            return self.update(key, value, tags)
        return self.add(key, value, tags)

    def delete(self, key: str, reason: str = "") -> MemoryEntry:
        """DELETE outdated/contradictory knowledge. Logs the reason."""
        data = self._load()
        if key not in data:
            raise KeyError(f"Key '{key}' does not exist.")
        old = data.pop(key)
        self._save(data)

        entry = MemoryEntry(
            key=key,
            value="",
            operation=MemoryOp.DELETE,
            reason=reason,
            previous_value=old.get("value", ""),
            tags=old.get("tags", []),
        )
        # Log the deletion
        self._del_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._del_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

        return entry

    def get(self, key: str) -> Optional[str]:
        """Get value by key, or None if not found."""
        data = self._load()
        if key in data:
            return data[key].get("value")
        return None

    def list_all(self) -> dict[str, str]:
        """List all key-value pairs."""
        return {k: v.get("value", "") for k, v in self._load().items()}

    def detect_conflicts(self) -> list[dict[str, Any]]:
        """Detect potential conflicts (keys with similar names or contradictory tags)."""
        data = self._load()
        conflicts: list[dict[str, Any]] = []
        keys = list(data.keys())

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                # Simple heuristic: check for substring overlap
                if k1 in k2 or k2 in k1:
                    conflicts.append({
                        "keys": [k1, k2],
                        "type": "similar_keys",
                        "values": [data[k1].get("value"), data[k2].get("value")],
                    })

        return conflicts

    def count(self) -> int:
        return len(self._load())

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict[str, Any]) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
