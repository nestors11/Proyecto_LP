from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Token:
    type: str
    value: Any
    line: int
    column: int
