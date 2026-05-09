from __future__ import annotations

from collections import defaultdict

_COUNTERS: dict[str, int] = defaultdict(int)


def next_number(key: str = "default") -> int:
    _COUNTERS[key] += 1
    return _COUNTERS[key]
