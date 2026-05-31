import pytest
import pytest
pytest.importorskip("networkx")

from voxel_graph import build_edges, to_networkx


def test_to_networkx_basic():
    points = [(0, 0), (1, 0), (0, 1)]
    edges = build_edges(points, connectivity=4)
    G = to_networkx(points, edges)
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 2
    assert G.nodes[0]["coord"] == (0, 0)


def test_to_networkx_with_attrs():
    points = [(0, 0), (1, 0)]
    edges = [(0, 1)]
    G = to_networkx(points, edges, node_attrs={"label": ["a", "b"]})
    assert G.nodes[0]["label"] == "a"
    assert G.nodes[1]["label"] == "b"


def test_to_pyg_shape():
    torch = pytest.importorskip("torch")
    from voxel_graph import to_pyg

    edges = [(0, 1), (1, 2)]
    edge_index = to_pyg(edges)
    assert edge_index.shape == (2, 2)
    assert edge_index.dtype == torch.long


def test_to_pyg_empty():
    torch = pytest.importorskip("torch")
    from voxel_graph import to_pyg

    edge_index = to_pyg([])
    assert edge_index.shape == (2, 0)
