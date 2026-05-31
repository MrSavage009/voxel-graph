import random

import pytest

from voxel_graph import build_edges
from voxel_graph.core import _VoxelGraphEngine


def test_2d_4_connectivity():
    points = [(0, 0), (1, 0), (0, 1), (1, 1)]
    edges = build_edges(points, connectivity=4)
    assert sorted(edges) == [(0, 1), (0, 2), (1, 3), (2, 3)]


def test_2d_8_connectivity():
    points = [(0, 0), (1, 0), (0, 1), (1, 1)]
    edges = build_edges(points, connectivity=8)
    assert sorted(edges) == [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def test_3d_6_connectivity():
    points = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    edges = build_edges(points, connectivity=6)
    assert sorted(edges) == [(0, 1), (0, 2), (0, 3)]


def test_3d_26_connectivity():
    points = [(0, 0, 0), (1, 1, 1)]
    edges = build_edges(points, connectivity=26)
    assert sorted(edges) == [(0, 1)]


def test_empty_points():
    assert build_edges([], connectivity=4) == []


def test_single_point():
    assert build_edges([(0, 0)], connectivity=4) == []


def test_custom_offsets():
    points = [(0, 0), (2, 0), (4, 0)]
    edges = build_edges(points, offsets=[(2, 0)])
    assert sorted(edges) == [(0, 1), (1, 2)]


def test_vs_brute_force_2d():
    random.seed(42)
    points = [
        (random.randint(-100, 100), random.randint(-100, 100))
        for _ in range(200)
    ]
    offsets = [
        (dx, dy)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        if not (dx == 0 and dy == 0)
    ]

    edges_lde = sorted(build_edges(points, offsets=offsets))

    n = len(points)
    edges_brute = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            if (dx, dy) in set(offsets):
                edges_brute.append((i, j))

    assert edges_lde == sorted(edges_brute)


def test_vs_brute_force_3d():
    random.seed(42)
    points = [
        (
            random.randint(-50, 50),
            random.randint(-50, 50),
            random.randint(-50, 50),
        )
        for _ in range(100)
    ]
    offsets = [
        (1, 0, 0),
        (-1, 0, 0),
        (0, 1, 0),
        (0, -1, 0),
        (0, 0, 1),
        (0, 0, -1),
    ]

    edges_lde = sorted(build_edges(points, offsets=offsets))

    n = len(points)
    edges_brute = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            dz = points[j][2] - points[i][2]
            if (dx, dy, dz) in set(offsets):
                edges_brute.append((i, j))

    assert edges_lde == sorted(edges_brute)


def test_engine_empty_points():
    engine = _VoxelGraphEngine([(1, 0, 0)])
    engine.build([])
    assert engine.find_pairs() == []


def test_engine_no_offsets():
    points = [(0, 0, 0), (1, 1, 1)]
    engine = _VoxelGraphEngine([])
    engine.build(points)
    assert engine.find_pairs() == []
    assert engine.packed == []  # Empty offsets -> early return
