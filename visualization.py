"""
visualization.py
Plots, heatmap and CSV export for the simulation (Task 2.3).

Every function takes a *finished* GridSimulation object (its time-series are
already populated) and either returns a matplotlib Figure (so the Colab UI can
display it inline) or writes a file. Keeping the functions Figure-returning
means the same code works headless (saved PNG) and interactively (Colab).

Module: Advanced Simulation Techniques (Task 2)
Author: Salina Khadka, BSBI Berlin
"""

import csv

import numpy as np
import matplotlib.pyplot as plt

from config import LINE_CAPACITIES, TOTAL_CAPACITY


# --------------------------------------------------------------------------- #
# 1. Generation vs demand
# --------------------------------------------------------------------------- #
def plot_power_output(sim):
    t = np.array(sim.ts["time"])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.stackplot(t, sim.ts["coal1"], sim.ts["coal2"], sim.ts["solar"],
                 labels=["Coal Gen 1 (300 MW)", "Coal Gen 2 (200 MW)",
                         "Solar Farm (150 MW)"],
                 colors=["#4a4a8a", "#7a7ac0", "#f5a623"], alpha=0.85)
    ax.plot(t, sim.ts["demand"], color="#e74c3c", linewidth=2.0,
            linestyle="--", label="Total Demand (MW)")
    ax.set_xlabel("Simulation Time (hours)")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Generator Power Output vs Demand", fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(0, sim.cfg["sim_duration"])
    ax.set_ylim(0, TOTAL_CAPACITY * 1.25)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# 2. Average line load % with overload thresholds
# --------------------------------------------------------------------------- #
def plot_grid_load(sim):
    t = np.array(sim.ts["time"])
    load = np.array(sim.ts["load_pct"])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(t, load, alpha=0.3, color="#2980b9")
    ax.plot(t, load, color="#2980b9", linewidth=1.5, label="Average line load %")
    ax.axhline(100, color="#e67e22", linewidth=1.5, linestyle="--",
               label="100% rated capacity")
    ax.axhline(sim.cfg["cascade_thresh"] * 100, color="#e74c3c",
               linewidth=2.0, linestyle="-.", label="Cascade threshold")
    for ft in sim.fail_times:
        ax.axvline(ft, color="#c0392b", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Simulation Time (hours)")
    ax.set_ylabel("Average Line Load (%)")
    ax.set_title("Grid Load Percentage Over Time", fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.set_xlim(0, sim.cfg["sim_duration"])
    ax.set_ylim(0, 160)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# 3. Failure-events timeline
# --------------------------------------------------------------------------- #
def plot_failures(sim):
    fig, ax = plt.subplots(figsize=(12, 3.5))
    if sim.fail_times:
        ml, sl, bl = ax.stem(sim.fail_times, [1] * len(sim.fail_times),
                             linefmt="#e74c3c", markerfmt="D", basefmt=" ")
        ml.set_markerfacecolor("#e74c3c")
        ml.set_markersize(8)
    ax.set_xlabel("Simulation Time (hours)")
    ax.set_title("Transmission Line Failure Events Timeline", fontweight="bold")
    ax.set_xlim(0, sim.cfg["sim_duration"])
    ax.set_ylim(0, 2)
    ax.set_yticks([])
    ax.grid(True, alpha=0.2, axis="x")
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# 4. Heatmap — per-line load % over time (Task 2.3 asks for heatmaps)
# --------------------------------------------------------------------------- #
def plot_line_heatmap(sim):
    line_ids = list(LINE_CAPACITIES.keys())
    matrix = np.array([sim.ts_line_pct[lid] for lid in line_ids])  # rows=lines

    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(matrix, aspect="auto", cmap="RdYlGn_r",
                   vmin=0, vmax=140, origin="lower",
                   extent=[0, sim.cfg["sim_duration"], -0.5, len(line_ids) - 0.5])
    ax.set_yticks(range(len(line_ids)))
    ax.set_yticklabels(line_ids)
    ax.set_xlabel("Simulation Time (hours)")
    ax.set_ylabel("Transmission Line")
    ax.set_title("Per-Line Load Heatmap (% of rated capacity)", fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, pad=0.01)
    cbar.set_label("Load (% of capacity)")
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# Saving helpers
# --------------------------------------------------------------------------- #
def save_all_figures(sim, prefix="graph_", outdir="."):
    """Save the four standard figures as PNGs. Returns the list of paths."""
    import os
    builders = {
        "power_output": plot_power_output,
        "grid_load":    plot_grid_load,
        "failures":     plot_failures,
        "heatmap":      plot_line_heatmap,
    }
    paths = []
    for name, builder in builders.items():
        fig = builder(sim)
        path = os.path.join(outdir, f"{prefix}{name}.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)
        paths.append(path)
    return paths


# --------------------------------------------------------------------------- #
# CSV export (Task 2.3 — "export results for further analysis")
# --------------------------------------------------------------------------- #
def export_timeseries_csv(sim, path="simulation_results.csv"):
    """Write the hourly time-series to a CSV file."""
    line_ids = list(LINE_CAPACITIES.keys())
    header = (["hour", "demand_MW", "coal1_MW", "coal2_MW", "solar_MW",
               "avg_load_pct", "lines_in_service"]
              + [f"{lid}_load_pct" for lid in line_ids])
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for i, hour in enumerate(sim.ts["time"]):
            row = [hour,
                   round(sim.ts["demand"][i], 2),
                   round(sim.ts["coal1"][i], 2),
                   round(sim.ts["coal2"][i], 2),
                   round(sim.ts["solar"][i], 2),
                   round(sim.ts["load_pct"][i], 2),
                   sim.ts["lines_up"][i]]
            row += [round(sim.ts_line_pct[lid][i], 2) for lid in line_ids]
            w.writerow(row)
    return path


def export_event_log_csv(sim, path="event_log.csv"):
    """Write the discrete event log (failures, cascades, restores) to CSV."""
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sim_hour", "event_type", "description"])
        for t, etype, msg in sim.event_log:
            w.writerow([round(t, 2), etype, msg])
    return path
