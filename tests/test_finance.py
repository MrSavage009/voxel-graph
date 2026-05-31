from voxel_graph.finance import build_tick_graph


def test_tick_graph_basic():
    trades = [(100, 1000), (101, 1001), (102, 1005)]
    edges = build_tick_graph(trades, price_radius=2, time_radius=5)
    assert sorted(edges) == [(0, 1), (0, 2), (1, 2)]


def test_tick_graph_empty():
    assert build_tick_graph([], price_radius=1, time_radius=1) == []


def test_tick_graph_single():
    assert build_tick_graph([(100, 1000)], price_radius=1, time_radius=1) == []
