from typing import List, Tuple

from .core import build_edges


def build_tick_graph(
    trades: List[Tuple[int, int]],
    price_radius: int = 2,
    time_radius: int = 5,
) -> List[Tuple[int, int]]:
    offsets = [
        (dx, dt)
        for dx in range(-price_radius, price_radius + 1)
        for dt in range(-time_radius, time_radius + 1)
        if not (dx == 0 and dt == 0)
    ]
    return build_edges(trades, offsets=offsets)
