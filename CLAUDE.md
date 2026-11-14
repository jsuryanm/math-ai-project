# Airport Networks: Task 4 (Connectivity and graph properties)

Group project on OpenFlights data (`data/*.dat`). Descriptive graph analysis only; no ML. See `README.md` for the six-task brief.

## Deliverable
`notebooks/04_connectivity_and_graph_properties.ipynb`: components, shortest paths, diameter, clustering, properties summary. Committed with executed outputs.

## Graph model (keep consistent across tasks)
- Nodes: airports by IATA code from `routes.dat` (3,425).
- Edges: undirected, duplicates collapsed, self-loops and `\N` codes dropped (19,256).
- Path metrics use the giant component (3,397 nodes, 99.2%), since distance is undefined across components.
- Distance = route hops, never km or travel time. The notebook shows hops correlate only weakly (0.35) with great-circle km.

## Key results
Avg path 4.10 hops, diameter 13, radius 7, avg clustering 0.487, transitivity 0.248 (random graph: ~0.003). 8 components.

## Run
Needs Python 3 with `networkx pandas matplotlib numpy nbformat nbconvert ipykernel`. Use a venv (system pip is PEP 668 locked).
Re-execute: `jupyter nbconvert --to notebook --execute --inplace notebooks/04_*.ipynb` (about 1 min; exact all-pairs BFS).

## Conventions
- Paths in the notebook are relative to `notebooks/` (`../data/`).
- Every plot gets a detailed reading plus a one-line **Brief**.
- Unlabeled airports in `airports.dat` lack city/country; coordinates cover 3,262 of 3,425 nodes.
- Keep changes minimal; state assumptions explicitly.
