"""
config.py
Configuration and system structure for the Smart Grid Cascading Failure simulation.

All tunable parameters live here so the model, the scenario runner and the
Colab user interface can share a single source of truth. Scenarios override
individual scalar values via a plain dict (see scenarios.py).

Module: Advanced Simulation Techniques (Task 2)
Author: Salina Khadka, BSBI Berlin
"""

# ---------------------------------------------------------------------------
# Physical grid structure (Task 2.1 — entities and relationships)
# ---------------------------------------------------------------------------

# Generators and their rated capacity in MW.
# Coal units are dispatchable baseload; the solar farm follows daylight.
GENERATORS = {
    "Coal Gen 1": {"capacity": 300, "type": "coal",  "dispatchable": True},
    "Coal Gen 2": {"capacity": 200, "type": "coal",  "dispatchable": True},
    "Solar Farm": {"capacity": 150, "type": "solar", "dispatchable": False},
}

# Transmission lines with rated thermal capacity in MW.
LINE_CAPACITIES = {
    "L1-A": 250,   # Coal Gen 1  -> Substation A
    "L2-A": 200,   # Coal Gen 2  -> Substation A
    "L3-B": 180,   # Solar Farm  -> Substation B
    "L4-C": 220,   # Substation A -> Substation C
    "L5-D": 160,   # Substation B -> Substation D
}

# Substations and the share of base demand drawn by their consumer zone.
SUBSTATIONS = {
    "Substation A": {"zone": "Zone 1: Industrial",  "base_load_frac": 0.40},
    "Substation B": {"zone": "Zone 2: Residential", "base_load_frac": 0.25},
    "Substation C": {"zone": "Zone 3: Commercial",  "base_load_frac": 0.20},
    "Substation D": {"zone": "Zone 4: Mixed",       "base_load_frac": 0.15},
}

# Total installed generation capacity (MW).
TOTAL_CAPACITY = sum(g["capacity"] for g in GENERATORS.values())  # 650 MW


# ---------------------------------------------------------------------------
# Default run parameters (the baseline scenario)
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "sim_duration":      72,     # simulation horizon in hours
    "time_step":         1,      # advance one simulated hour per step
    "base_fail_prob":    0.05,   # per-line failure probability per hour at normal load
    "cascade_thresh":    1.20,   # >120% of rated capacity triggers a cascade
    "overload_fail_mult": 5.0,   # failure-probability multiplier when overloaded
    "repair_time_min":   2.0,    # minimum repair duration (sim hours)
    "repair_time_max":   4.0,    # maximum repair duration (sim hours)
    "num_repair_crews":  1,      # repair crews available (a SimPy resource)
    "demand_multiplier": 1.0,    # global scaling of demand (scenario lever)
    "solar_scale":       1.0,    # global scaling of solar output (scenario lever)
    "seed":              42,     # RNG seed for reproducibility
}


def make_config(**overrides):
    """Return a fresh copy of DEFAULT_CONFIG with the given keys overridden."""
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(overrides)
    return cfg
