import numpy as np

from voxel_graph import build_edges, to_networkx

np.random.seed(42)
scan = np.random.rand(50, 50, 50)
scan[20:30, 20:30, 20:30] += 0.5

threshold = 0.7
voxels = np.argwhere(scan > threshold).tolist()
intensities = scan[scan > threshold].tolist()

print(f"Voxels above threshold: {len(voxels)}")

edges = build_edges(voxels, connectivity=6)
G = to_networkx(voxels, edges, node_attrs={"intensity": intensities})

print(f"Graph nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
