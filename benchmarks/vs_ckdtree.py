import time
import random

import numpy as np
from scipy.spatial import cKDTree

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


def ckdtree_exact_edges(points, offsets):
    dim = len(points[0])
    pts = np.array(points, dtype=float)
    tree = cKDTree(pts)
    max_radius = max(np.sqrt(sum(d ** 2 for d in off)) for off in offsets) + 0.01
    offset_set = set(offsets)

    pairs = []
    for i, p in enumerate(pts):
        neighbors = tree.query_ball_point(p, r=max_radius)
        for j in neighbors:
            if j > i:
                diff = tuple(int(pts[j][k] - pts[i][k]) for k in range(dim))
                if diff in offset_set:
                    pairs.append((i, j))
    return sorted(pairs)


def benchmark():
    print("3D 6-connectivity: voxel-graph vs cKDTree")
    print(f"{'n':>8} {'cKDTree (s)':>14} {'voxel-graph (s)':>16} {'ratio':>10} {'edges':>10}")
    print("-" * 65)

    for n in [1000, 5000, 10000]:
        points = generate_random_points(n, dim=3)
        offsets = [
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        ]

        t0 = time.perf_counter()
        edges_ckd = ckdtree_exact_edges(points, offsets)
        t_ckd = time.perf_counter() - t0

        t0 = time.perf_counter()
        edges_vg = build_edges(points, offsets=offsets)
        t_vg = time.perf_counter() - t0

        assert sorted(edges_vg) == edges_ckd

        ratio = t_ckd / t_vg if t_vg > 0 else float("inf")
        print(
            f"{n:8d} {t_ckd:14.4f} {t_vg:16.4f} {ratio:10.1f} {len(edges_ckd):10d}"
        )


if __name__ == "__main__":
    benchmark()
