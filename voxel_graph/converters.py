from typing import Any, Dict, List, Tuple, Union


def to_pyg(edges: List[Tuple[int, int]]):
    try:
        import torch
    except ImportError:
        raise ImportError(
            "torch is required for to_pyg. Install with: pip install torch"
        )
    if not edges:
        return torch.zeros((2, 0), dtype=torch.long)
    return torch.tensor(edges, dtype=torch.long).t().contiguous()


def to_networkx(
    coordinates: List[Tuple[int, ...]],
    edges: List[Tuple[int, int]],
    node_attrs: Union[Dict[str, List[Any]], None] = None,
):
    import networkx as nx

    G = nx.Graph()
    for i, coord in enumerate(coordinates):
        d = {"coord": coord}
        if node_attrs:
            for key, vals in node_attrs.items():
                d[key] = vals[i]
        G.add_node(i, **d)
    G.add_edges_from(edges)
    return G
