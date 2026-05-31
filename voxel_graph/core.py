import math
from collections import defaultdict
from typing import List, Tuple, Union


class _VoxelGraphEngine:
    def __init__(self, offsets: List[Tuple[int, ...]]):
        self.offsets = list(dict.fromkeys(offsets))
        self.dim = len(self.offsets[0]) if self.offsets else 3
        self.modulus = 1
        self.coords: List[Tuple[int, ...]] = []
        self.packed: List[int] = []
        self.buckets: defaultdict = defaultdict(list)
        self.stride = 1

    def build(self, points: List[Tuple[int, ...]]) -> None:
        self.coords = points
        n = len(points)
        if n == 0 or not self.offsets:
            self.modulus = 1
            self.buckets = defaultdict(list)
            self.packed = []
            self.stride = 1
            return

        self.modulus = int(math.isqrt(n)) + 1

        for idx, p in enumerate(points):
            key = tuple(c % self.modulus for c in p)
            self.buckets[key].append(idx)

        if self.dim == 2:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            stride = max(max(xs) - min(xs), max(ys) - min(ys)) + 1
            sx, sy = -min(xs), -min(ys)
            self.packed = [(x + sx) * stride + (y + sy) for x, y in points]
            self.stride = stride
        else:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            zs = [p[2] for p in points]
            stride = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) + 1
            sx, sy, sz = -min(xs), -min(ys), -min(zs)
            self.packed = [
                ((x + sx) * stride + (y + sy)) * stride + (z + sz)
                for x, y, z in points
            ]
            self.stride = stride

    def _process_offset(self, offset: Tuple[int, ...]) -> List[Tuple[int, int]]:
        pairs = []
        for i, p in enumerate(self.coords):
            key = tuple((c + dc) % self.modulus for c, dc in zip(p, offset))
            for j in self.buckets.get(key, []):
                if j > i:
                    if self.dim == 2:
                        dx, dy = offset
                        expected = dx * self.stride + dy
                    else:
                        dx, dy, dz = offset
                        expected = dx * self.stride ** 2 + dy * self.stride + dz
                    if self.packed[j] - self.packed[i] == expected:
                        pairs.append((i, j))
        return pairs

    def find_pairs(self) -> List[Tuple[int, int]]:
        return [p for off in self.offsets for p in self._process_offset(off)]


def _connectivity_offsets(connectivity: int, dim: int) -> List[Tuple[int, ...]]:
    if dim == 2:
        if connectivity == 4:
            return [(1, 0), (-1, 0), (0, 1), (0, -1)]
        elif connectivity == 8:
            return [
                (dx, dy)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if not (dx == 0 and dy == 0)
            ]
    elif dim == 3:
        if connectivity == 6:
            return [
                (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)
            ]
        elif connectivity == 26:
            return [
                (dx, dy, dz)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                for dz in (-1, 0, 1)
                if not (dx == 0 and dy == 0 and dz == 0)
            ]
    raise ValueError(f"Unsupported connectivity={connectivity} for dim={dim}")


def build_edges(
    coordinates: List[Tuple[int, ...]],
    connectivity: Union[int, None] = None,
    offsets: Union[List[Tuple[int, ...]], None] = None,
) -> List[Tuple[int, int]]:
    if not coordinates:
        return []

    dim = len(coordinates[0])

    if offsets is not None:
        off = offsets
    elif connectivity is not None:
        off = _connectivity_offsets(connectivity, dim)
    else:
        raise ValueError("Provide either connectivity or offsets")

    engine = _VoxelGraphEngine(off)
    engine.build(coordinates)
    return engine.find_pairs()
