# Smart Grid Cascading-Failure Simulation

**Module:** Advanced Simulation Techniques (AST) — Task 2: Simulation Design and Implementation
**Author:** Salina Khadka, BSBI Berlin
**Tool:** Python + [SimPy](https://simpy.readthedocs.io/) (discrete-event simulation)

A discrete-event simulation of power-system stability and cascading-failure dynamics in a
resilient smart grid. The model captures demand variability, renewable (solar) intermittency,
transmission-line overload, stochastic line failures, load redistribution, cascading
failures, and repair-crew recovery — and evaluates resilience across several what-if
scenarios.

## ▶ Run it in Google Colab (no installation)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/khadkasaleena/smart-grid-simulation/blob/main/Smart_Grid_Simulation_Colab.ipynb)

Click the badge, then run the cells top to bottom. The **Setup** cell installs SimPy and clones
this repository so the model files are available. The interactive control panel lets you adjust
parameters with sliders, view the plots and heatmap inline, and export results to CSV.

## Repository contents

| File | Role |
|------|------|
| `config.py` | Grid structure (generators, lines, substations) and tunable default parameters |
| `grid_model.py` | The core discrete-event `GridSimulation` class and its SimPy processes |
| `metrics.py` | Headline-metric summary and the multi-seed accuracy (confidence-interval) study |
| `scenarios.py` | Six predefined what-if scenarios and the comparison runner |
| `visualization.py` | Plots, per-line heatmap, and CSV export functions |
| `make_system_diagram.py` | Generates the conceptual system diagram (`system_diagram.png`) |
| `run_simulation.py` | Command-line entry point that runs everything and saves all outputs |
| `Smart_Grid_Simulation_Colab.ipynb` | Interactive Google Colab notebook (the user interface) |

## Run locally

```bash
pip install -r requirements.txt
python run_simulation.py        # baseline run, figures, CSVs, scenario table, accuracy study
python make_system_diagram.py   # regenerate the system diagram
```

## Modelling approach

Discrete-event simulation is the natural fit: the grid is driven by **discrete events**
(line overloads, failures, repair completions) interleaved with hourly sampling of the
continuous demand/generation profiles. SimPy's process-based model expresses the concurrent
behaviour of generators, demand, per-line monitors and the shared repair crew (a `Resource`)
clearly and reproducibly. See the accompanying report for the full justification (Task 1.3)
and a comparison against system-dynamics and agent-based alternatives (Task 3).

## Outputs

- `graph_power_output.png` — stacked generation vs demand
- `graph_grid_load.png` — average line load % with overload/cascade thresholds
- `graph_failures.png` — failure-event timeline
- `graph_heatmap.png` — per-line load heatmap
- `simulation_results.csv`, `event_log.csv`, `scenario_comparison.csv` — exported data
