"""
run_simulation.py
Command-line entry point that ties everything together.

Running `python run_simulation.py` will:
  1. run the baseline scenario and print its metrics,
  2. save the four figures (power, load, failures, heatmap) as PNGs,
  3. export the time-series and event log to CSV,
  4. run every what-if scenario and print a comparison table,
  5. run a multi-seed accuracy study and print mean +/- 95% CI.

Module: Advanced Simulation Techniques (Task 2)
Author: Salina Khadka, BSBI Berlin
"""

import os

import matplotlib
matplotlib.use("Agg")   # headless backend for the CLI run

from grid_model import GridSimulation
from metrics import summarise, accuracy_study, print_accuracy_report
from visualization import (save_all_figures, export_timeseries_csv,
                           export_event_log_csv)
from scenarios import run_all, print_comparison, export_comparison_csv

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("=" * 60)
    print("  SMART GRID CASCADING FAILURE SIMULATION")
    print("=" * 60)

    # --- 1. Baseline run -------------------------------------------------
    sim = GridSimulation(seed=42)
    results = sim.run()
    print("\nBaseline metrics:")
    for k, v in summarise(results).items():
        print(f"  {k:18s}: {v}")

    # --- 2. Figures ------------------------------------------------------
    print("\nSaving figures...")
    for p in save_all_figures(sim, outdir=OUTDIR):
        print(f"  saved {os.path.basename(p)}")

    # --- 3. CSV exports --------------------------------------------------
    ts_csv = export_timeseries_csv(sim, os.path.join(OUTDIR, "simulation_results.csv"))
    ev_csv = export_event_log_csv(sim, os.path.join(OUTDIR, "event_log.csv"))
    print(f"  exported {os.path.basename(ts_csv)} and {os.path.basename(ev_csv)}")

    # --- 4. Scenario comparison -----------------------------------------
    print("\nScenario comparison:")
    rows = run_all(seed=42)
    print_comparison(rows)
    cmp_csv = export_comparison_csv(rows, os.path.join(OUTDIR, "scenario_comparison.csv"))
    print(f"\n  exported {os.path.basename(cmp_csv)}")

    # --- 5. Accuracy study ----------------------------------------------
    report = accuracy_study(n_runs=30)
    print_accuracy_report(report)

    print("\nDone.")


if __name__ == "__main__":
    main()
