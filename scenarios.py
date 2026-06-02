"""
scenarios.py
Defines and runs the alternative "what-if" scenarios (Task 2.4).

Each scenario is just a name plus a dict of config overrides. Running them all
through the same model and comparing the headline metrics is what lets us study
how demand growth, ageing infrastructure or extra repair crews change the grid's
resilience.

Module: Advanced Simulation Techniques (Task 2)
Author: Salina Khadka, BSBI Berlin
"""

from grid_model import GridSimulation
from metrics import summarise


# name -> (description, config overrides)
SCENARIOS = {
    "Baseline": (
        "Normal demand, single repair crew",
        {},
    ),
    "High Demand": (
        "Demand +25% (e.g. heatwave / load growth)",
        {"demand_multiplier": 1.25},
    ),
    "Aged Infrastructure": (
        "Failure probability tripled (ageing assets)",
        {"base_fail_prob": 0.15},
    ),
    "High Renewable": (
        "Solar capacity factor boosted, demand normal",
        {"solar_scale": 1.4},
    ),
    "Extra Repair Crews": (
        "Three repair crews instead of one",
        {"num_repair_crews": 3},
    ),
    "Stress Test": (
        "High demand AND aged infrastructure together",
        {"demand_multiplier": 1.25, "base_fail_prob": 0.15},
    ),
}


def run_scenario(name, seed=42):
    """Run a single named scenario and return its summarised metrics."""
    if name not in SCENARIOS:
        raise KeyError(f"Unknown scenario: {name}")
    _desc, overrides = SCENARIOS[name]
    sim = GridSimulation(config=overrides, seed=seed)
    results = sim.run()
    return sim, results


def run_all(seed=42):
    """Run every scenario and return an ordered list of summary rows."""
    rows = []
    for name, (desc, overrides) in SCENARIOS.items():
        sim = GridSimulation(config=overrides, seed=seed)
        results = sim.run()
        row = {"scenario": name, "description": desc}
        row.update(summarise(results))
        rows.append(row)
    return rows


def print_comparison(rows):
    """Print a tidy comparison table of all scenarios."""
    cols = ["scenario", "failures", "cascade_events", "mttr_h",
            "peak_load_pct", "crew_utilisation", "unrecovered", "exec_ms"]
    widths = {c: max(len(c), max(len(str(r[c])) for r in rows)) for c in cols}
    header = "  ".join(c.ljust(widths[c]) for c in cols)
    print(header)
    print("-" * len(header))
    for r in rows:
        print("  ".join(str(r[c]).ljust(widths[c]) for c in cols))


def export_comparison_csv(rows, path="scenario_comparison.csv"):
    import csv
    cols = ["scenario", "description", "failures", "recoveries", "unrecovered",
            "cascade_events", "mttr_h", "peak_load_pct", "crew_utilisation",
            "exec_ms"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    return path
