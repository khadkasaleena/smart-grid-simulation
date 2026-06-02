"""
metrics.py
Performance and accuracy metrics for the simulation (Task 2.4).

Provides:
  * summarise()        — pretty one-line dict of headline metrics for a run
  * accuracy_study()   — repeat the same scenario across many seeds and report
                         the mean and a 95% confidence half-width. Because the
                         model is stochastic, this confidence interval is our
                         "accuracy measure": it tells us how trustworthy a
                         single run's numbers are.

Module: Advanced Simulation Techniques (Task 2)
Author: Salina Khadka, BSBI Berlin
"""

import math

from grid_model import GridSimulation


def summarise(results):
    """Return a flat dict of the headline metrics for one run."""
    return {
        "failures":         results["failures"],
        "recoveries":       results["recoveries"],
        "unrecovered":      results["unrecovered"],
        "cascade_events":   results["cascade_events"],
        "mttr_h":           round(results["mttr"], 2),
        "peak_load_pct":    round(results["peak_load_pct"], 1),
        "crew_utilisation": round(results["crew_utilisation"], 3),
        "exec_ms":          round(results["exec_ms"], 2),
    }


def _mean_std(values):
    n = len(values)
    mean = sum(values) / n
    if n < 2:
        return mean, 0.0
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return mean, math.sqrt(var)


def accuracy_study(config=None, n_runs=30, base_seed=1000):
    """
    Run the same configuration with `n_runs` different seeds and report the
    mean and 95% confidence half-width for the key output metrics.

    Returns a dict: metric -> {"mean", "std", "ci95", "n"}.
    The 95% CI half-width is 1.96 * std / sqrt(n).
    """
    collected = {"failures": [], "cascade_events": [], "mttr": [],
                 "peak_load_pct": [], "crew_utilisation": []}

    for i in range(n_runs):
        sim = GridSimulation(config=config, seed=base_seed + i)
        r = sim.run()
        collected["failures"].append(r["failures"])
        collected["cascade_events"].append(r["cascade_events"])
        collected["mttr"].append(r["mttr"])
        collected["peak_load_pct"].append(r["peak_load_pct"])
        collected["crew_utilisation"].append(r["crew_utilisation"])

    report = {}
    for metric, values in collected.items():
        mean, std = _mean_std(values)
        ci95 = 1.96 * std / math.sqrt(n_runs) if n_runs > 1 else 0.0
        report[metric] = {"mean": mean, "std": std, "ci95": ci95, "n": n_runs}
    return report


def print_accuracy_report(report):
    print("\nAccuracy study (mean +/- 95% CI across "
          f"{next(iter(report.values()))['n']} seeds)")
    print("-" * 56)
    for metric, s in report.items():
        print(f"  {metric:18s}: {s['mean']:8.3f}  +/- {s['ci95']:.3f}")
    print("-" * 56)
