# voxel-graph

[![PyPI](https://img.shields.io/pypi/v/voxel-graph)](https://pypi.org/project/voxel-graph/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Exact sparse lattice neighbor search in pure Python — 12KB, zero compilation, zero dependencies.**

This is not a replacement for `scipy.spatial.cKDTree`, `faiss`, or `torch_cluster`. Those libraries are faster, more general, and better maintained. They are also heavy, compiled, and often impossible to install in constrained environments.

`voxel-graph` exists for the edge cases where the heavy tools fail:

- You need **exact integer offsets**, not approximate Euclidean radius queries.
- You are running on a **Raspberry Pi, embedded controller, or browser WASM** where `scipy` won't compile.
- You are **prototyping a paper or architecture** and need working code in 30 seconds, not 30 minutes of dependency resolution.
- You are **teaching spatial algorithms** and need readable, benchmarked, self-contained code.
- You are building **serverless functions** with a 250MB deployment package limit.

If you have `scipy` and `torch` installed, use those. If you don't — or can't — use this.

---

## What it does

Given a list of integer coordinates on a lattice (e.g., voxelized point clouds, discretized sensor grids, tick data) and a fixed set of offset vectors, find all unordered pairs `(i, j)` where `coordinates[j] - coordinates[i]` is exactly one of the allowed offsets.

- **Time complexity:** `O(n * |U| * bucket_size)`. For sparse data, `bucket_size ~ 1`, so effectively `O(n)`.
- **Space complexity:** `O(n)` for the hash table.
- **Correctness:** Verified against brute-force `O(n^2)` ground truth on every release.

---

## Install

```bash
pip install voxel-graph
```

Hard dependency: `numpy` only.

Optional: `torch` (for `to_pyg`), `networkx` (for `to_networkx`), `scipy` (for benchmark comparisons).

---

## Quick start

```python
from voxel_graph import build_edges

# Integer coordinates only
voxels = [(12, 45, 3), (12, 46, 3), (13, 45, 3), ...]

# 6-connectivity (face neighbors) or 26-connectivity (full cube)
edges = build_edges(voxels, connectivity=6)

# Returns: [(0, 1), (0, 2), ...]  -- index pairs into your input list
```

---

## Five use cases (honest assessment)

### 1. Academic reproducibility

**You are:** A researcher publishing a paper on percolation, lattice-based cryptography, or spatial graph theory. Reviewers demand reproducible code. You need a reference implementation that is small enough to include as supplementary material and clear enough to verify by inspection.

**Why not scipy:** Your algorithm depends on exact lattice offsets, not Euclidean distance. `cKDTree` query + post-filter is conceptually messy in a methods section. You want code that maps 1:1 to your paper's pseudocode.

**Why this:** 200 lines of pure Python. No black boxes. The spatial hash logic is exposed and documented. Reviewers can read it in one sitting.

```python
from voxel_graph import build_edges

# Reproduce Figure 3 from your paper
voxels = load_simulation_data()
edges = build_edges(voxels, offsets=[(1,0,0), (-1,0,0), (0,1,0), (0,-1,0)])
G = nx.Graph()
G.add_edges_from(edges)
# ... compute percolation threshold
```

---

### 2. ML prototyping before CUDA commitment

**You are:** A machine learning engineer experimenting with a new 3D GNN architecture. You want to know if graph connectivity pattern matters before spending a day writing CUDA kernels and fighting `torch_sparse` compilation.

**Why not torch_cluster:** It requires matching PyTorch, CUDA, and OS versions. On a fresh machine, `pip install torch-scatter` can take 45 minutes and still fail. You want to test your idea in a Jupyter notebook now.

**Why this:** `pip install voxel-graph` takes 3 seconds. `build_edges()` returns a Python list you can convert to `torch.tensor` manually. Your architecture experiment runs in minutes, not hours.

```python
from voxel_graph import build_edges, to_pyg

voxels = voxelize_lidar(points, voxel_size=0.1)
edges = build_edges(voxels, connectivity=26)
edge_index = to_pyg(edges)  # torch.tensor of shape [2, num_edges]

# Feed to your experimental GNN
out = model(x, edge_index)
```

**Limitation:** This is for prototyping only. If your architecture works, you will rewrite the neighbor search in CUDA. This package buys you time, not performance.

---

### 3. Embedded and edge devices

**You are:** An IoT developer with a Raspberry Pi, microcontroller, or industrial PLC running Python (or MicroPython). You need to find neighbors in a sensor grid. You cannot install `scipy` (150MB, requires compilation) or `torch` (impossible on most embedded targets).

**Why not scipy:** It does not compile on ARM without a full toolchain. It exceeds the storage budget of most microcontrollers. It is overkill for finding adjacent cells in a 50x50 temperature sensor grid.

**Why this:** Pure Python. Works on any Python interpreter with `numpy`. 12KB installed size. No C compiler, no wheel hunting, no version matching.

```python
from voxel_graph import build_edges

# Temperature sensor grid: (x, y) integer positions
sensors = [(i, j) for i in range(50) for j in range(50) if sensor_active(i, j)]

# Find adjacent sensors for heat diffusion model
edges = build_edges(sensors, connectivity=4)
```

---

### 4. Browser and serverless Python

**You are:** Building a web-based data tool with Pyodide (Python in WebAssembly) or an AWS Lambda function with a 250MB deployment package limit. You need spatial neighbor search inside the browser or in a cold-started function.

**Why not scipy:** Pyodide can load `scipy`, but it adds 30MB to the initial download. AWS Lambda layers with `scipy` are 150MB, leaving no room for your actual application. Cold start latency kills user experience.

**Why this:** 12KB. Downloads in milliseconds. No C extensions to load. Works in Pyodide's restricted WASM environment where `ctypes` and compiled extensions are limited.

```python
from voxel_graph import build_edges

# Running in Pyodide inside the browser
voxels = js.getVoxelData()  # From JavaScript
edges = build_edges(voxels, connectivity=6)
# Render graph with D3.js
```

---

### 5. Teaching and interview preparation

**You are:** A CS instructor teaching spatial data structures, or a student preparing for quant/ML interviews where you must implement fast neighbor search from scratch.

**Why not leetcode:** LeetCode solutions are fragments. They don't show benchmarking, edge cases, packaging, or real-world integration. You need a complete, runnable project.

**Why this:** The entire algorithm is ~200 lines. It includes a spatial hash, bit-packing for exact matching, and a verified A/B benchmark against brute force. You can read it in one sitting, modify it, and explain it in an interview.

```python
# Interview question: "Implement fast 3D grid neighbor search"
from voxel_graph.core import _VoxelGraphEngine

# The entire algorithm is exposed. Read the source, understand the hash,
# then explain why it's O(n) for sparse data and O(n^2) in the worst case.
```

---

## Benchmarks

Exact 26-connectivity on random 3D integer lattices. Verified against brute-force ground truth.

| Voxels | Brute O(n^2) (s) | **voxel-graph (s)** | Speedup | Edges |
|--------|-----------------|---------------------|---------|-------|
| 1,000 | 0.24 | **0.04** | 6.7x | 0 |
| 5,000 | 6.19 | **0.17** | 34.3x | 1 |
| 10,000 | 23.80 | **0.36** | 68.9x | 6 |
| 50,000 | ~2,500* | **1.90** | ~1,300x | 138 |

*Estimated from quadratic scaling.

**A/B test methodology:**
1. Generate `n` random integer coordinates in a `1000^3` lattice.
2. Offsets: 26-connectivity.
3. Ground truth: brute-force `O(n^2)` double loop.
4. Assert: `sorted(brute_edges) == sorted(voxel_graph_edges)`.
5. Measure: wall-clock time, single run.

**When this benchmark matters:** When you are comparing against brute force because you have no other option. When you have `scipy` installed, compare against `cKDTree` instead — it will win on float data, lose on exact integer offsets.

---

## API

### `build_edges(coordinates, connectivity=None, offsets=None)`
- `coordinates`: list of `(x, y)` or `(x, y, z)` integer tuples.
- `connectivity`: `4` or `8` for 2D; `6` or `26` for 3D. Mutually exclusive with `offsets`.
- `offsets`: custom list of `(dx, dy)` or `(dx, dy, dz)` vectors. Overrides `connectivity`.
- Returns: list of `(i, j)` index pairs with `j > i`.

### `to_pyg(edges)`
- Converts edge list to `torch.tensor` of shape `[2, num_edges]`.
- Requires `torch` installed.

### `to_networkx(coordinates, edges, node_attrs=None)`
- Returns a `networkx.Graph` with node attributes `coord` and any custom attrs.

### `build_tick_graph(trades, price_radius=2, time_radius=5)`
- `trades`: list of `(price_tick, time_ms)` integer tuples.
- Returns edge list for market microstructure analysis.

---

## Requirements

- Python 3.8+
- `numpy` (only hard dependency)

Optional:
- `torch` for `to_pyg`
- `networkx` for `to_networkx`
- `scipy` for benchmark comparisons

---

## When not to use this

| Situation | Use instead |
|-----------|-------------|
| Float coordinates, approximate neighbors | `scipy.spatial.cKDTree`, `sklearn.neighbors` |
| High-dimensional data (d > 3) | `faiss`, `annoy`, `hnswlib` |
| GPU-accelerated batch processing | `torch_cluster.radius_graph`, `MinkowskiEngine` |
| Dense grid where every cell exists | `networkx.grid_graph`, `scipy.ndimage` |
| Production at scale | Rewrite in C++/CUDA |

---

## License

MIT

---

## Contributing

Pull requests welcome. Please add tests and ensure `pytest` passes. If you have a new use case for constrained environments, open an issue with a description of your target platform and its limitations (e.g., "MicroPython on ESP32 with 512KB RAM").
