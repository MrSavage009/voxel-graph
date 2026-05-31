import random

from voxel_graph import build_edges, to_pyg

random.seed(42)
voxels = [
    (random.randint(0, 200), random.randint(0, 200), random.randint(0, 50))
    for _ in range(10000)
]

edges = build_edges(voxels, connectivity=26)
print(f"Found {len(edges)} edges among {len(voxels)} voxels")

edge_index = to_pyg(edges)
print(f"edge_index shape: {edge_index.shape}")
