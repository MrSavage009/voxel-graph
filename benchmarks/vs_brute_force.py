import time
import random

from voxel_graph import build_edges


def generate_random_points(n, dim=3, low=-500, high=500):
    if dim == 2:
        return [
            (random.randint(low, high), random.randint(low, high))
            for _ in range(n)
        ]
    return [
        (
            random.randint(low, high),
            random.randint(low, high),
            random.randint(low, high),
        )
        for _ in range(n)
    ]


def brute_force_edges(points, offsets):
    n = len(points)
    edges = []
    dim = len(points[0])
    offset_set = set(offsets)
    for i in range(n):
        for j in range(i + 1, n):
            diff = tuple(points[j][k] - points[i][k] for k in range(dim))
            if diff in offset_set:
                edges.append((i, j))
    return edges


def benchmark():
    print("3D 26-connectivity: voxel-graph vs brute-force")
    print(f"{'n':>8} {'brute (s)':>12} {'voxel-graph (s)':>16} {'speedup':>10} {'edges':>10}")
    print("-" * 60)

    for n in [1000, 2000, 5000, 10000]:
        points = generate_random_points(n, dim=3)
        offsets = [
            (dx, dy, dz)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            for dz in (-1, 0, 1)
            if not (dx == 0 and dy == 0 and dz == 0)
        ]

        t0 = time.perf_counter()
        edges_brute = brute_force_edges(points, offsets)
        t_brute = time.perf_counter() - t0

        t0 = time.perf_counter()
        edges_fast = build_edges(points, offsets=offsets)
        t_fast = time.perf_counter() - t0

        assert sorted(edges_fast) == sorted(edges_brute)

        speedup = t_brute / t_fast if t_fast > 0 else float("inf")
        print(
            f"{n:8d} {t_brute:12.4f} {t_fast:16.4f} {speedup:10.1f} {len(edges_brute):10d}"
        )


if __name__ == "__main__":
    benchmark()
