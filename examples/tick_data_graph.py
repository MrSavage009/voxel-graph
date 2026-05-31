from voxel_graph.finance import build_tick_graph

trades = [
    (10045, 2300),
    (10046, 2301),
    (10047, 2302),
    (10048, 2310),
    (10045, 2315),
    (10050, 2320),
]

edges = build_tick_graph(trades, price_radius=2, time_radius=5)
print(f"Correlated trade pairs: {edges}")
