"""Strict JSON parsing shared by validation and execution."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def _parse_finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"JSON number is outside the finite float range: {value}")
    return parsed


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def parse_json(text: str) -> Any:
    """Parse strict, finite JSON and reject duplicate object keys."""
    return json.loads(
        text,
        parse_constant=_reject_nonstandard_constant,
        parse_float=_parse_finite_float,
        object_pairs_hook=_reject_duplicate_keys,
    )


def load_json(path: Path) -> Any:
    """Read and parse one strict JSON file."""
    return parse_json(path.read_text(encoding="utf-8"))
