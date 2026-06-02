"""
grid_model.py
The discrete-event SimPy model of the smart grid (Task 2.2).

The whole simulation is wrapped in a GridSimulation class so that each run owns
its own random-number generator and state. This isolation is what makes the
multi-scenario sweep in scenarios.py reproducible — no global state leaks
between runs.

Concurrent SimPy processes:
  * generator_process   — sets generator output every hour
  * demand_process      — sets total demand every hour (time-of-day profile)
  * line_monitor        — one per transmission line: checks overload/failure
  * repair_process      — spawned on failure; competes for the repair crew
  * metrics_collector   — samples the system state every hour for plotting

Module: Advanced Simulation Techniques (Task 2)
Author: Salina Khadka, BSBI Berlin
"""

import math
import random
import time as wall_clock

import simpy

from config import (
    GENERATORS,
    LINE_CAPACITIES,
    TOTAL_CAPACITY,
    make_config,
)


class GridSimulation:
    """A single, self-contained run of the smart-grid cascading-failure model."""

    def __init__(self, config=None, seed=None):
        # Merge caller overrides onto the defaults.
        self.cfg = make_config(**(config or {}))
        if seed is not None:
            self.cfg["seed"] = seed

        # Dedicated RNG -> reproducible and isolated from other runs.
        self.rng = random.Random(self.cfg["seed"])

        # --- Mutable grid state -------------------------------------------
        self.gen_output = {name: 0.0 for name in GENERATORS}
        self.line_loads = {lid: 0.0 for lid in LINE_CAPACITIES}
        self.line_status = {lid: True for lid in LINE_CAPACITIES}   # True = in service
        self.demand = 0.0

        # --- Counters -----------------------------------------------------
        self.failures = 0
        self.recoveries = 0
        self.cascade_events = 0
        self.repair_times = []          # actual outage durations (sim hours)
        self.crew_busy_hours = 0.0      # for repair-crew utilisation
        self.event_log = []             # (time, type, message)

        # --- Time-series for plotting / export ----------------------------
        self.ts = {
            "time": [], "coal1": [], "coal2": [], "solar": [],
            "demand": [], "load_pct": [], "lines_up": [],
        }
        # Per-line load% history -> used for the heatmap (Task 2.3).
        self.ts_line_pct = {lid: [] for lid in LINE_CAPACITIES}
        self.fail_times = []            # sim hours at which failures occur

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    def log(self, env, etype, msg):
        self.event_log.append((env.now, etype, msg))

    # ------------------------------------------------------------------ #
    # Demand and solar profiles
    # ------------------------------------------------------------------ #
    def demand_fraction(self, hour):
        """Demand as a fraction of TOTAL_CAPACITY, by time of day (+/-5% jitter)."""
        h = hour % 24
        if 23 <= h or h < 6:
            base = 0.60                      # overnight trough
        elif (6 <= h < 8) or (20 <= h < 23):
            base = 0.85                      # shoulder
        elif (8 <= h < 10) or (17 <= h < 20):
            base = 1.10                      # morning / evening peak
        else:
            base = 0.90                      # daytime standard
        jitter = self.rng.uniform(-0.05, 0.05)
        return (base + jitter) * self.cfg["demand_multiplier"]

    def solar_output(self, hour, capacity):
        """Sinusoidal daylight curve scaled by random cloud cover."""
        h = hour % 24
        if 6.0 <= h <= 20.0:
            sun = math.sin(math.pi * (h - 6) / 14)
            cloud = self.rng.uniform(0.55, 1.0)
            return capacity * sun * cloud * self.cfg["solar_scale"]
        return 0.0

    # ------------------------------------------------------------------ #
    # Load distribution
    # ------------------------------------------------------------------ #
    def distribute_load(self):
        """Spread current demand across in-service lines, proportional to capacity."""
        active = [lid for lid, up in self.line_status.items() if up]
        if not active:
            for lid in LINE_CAPACITIES:
                self.line_loads[lid] = 0.0
            return
        total_active_cap = sum(LINE_CAPACITIES[lid] for lid in active)
        for lid in LINE_CAPACITIES:
            if self.line_status[lid]:
                share = LINE_CAPACITIES[lid] / total_active_cap
                self.line_loads[lid] = self.demand * share
            else:
                self.line_loads[lid] = 0.0

    # ------------------------------------------------------------------ #
    # SimPy processes
    # ------------------------------------------------------------------ #
    def generator_process(self, env):
        c1 = GENERATORS["Coal Gen 1"]["capacity"]
        c2 = GENERATORS["Coal Gen 2"]["capacity"]
        cs = GENERATORS["Solar Farm"]["capacity"]
        while True:
            self.gen_output["Coal Gen 1"] = c1
            self.gen_output["Coal Gen 2"] = c2
            self.gen_output["Solar Farm"] = self.solar_output(env.now, cs)
            yield env.timeout(self.cfg["time_step"])

    def demand_process(self, env):
        while True:
            self.demand = TOTAL_CAPACITY * self.demand_fraction(env.now)
            yield env.timeout(self.cfg["time_step"])

    def repair_process(self, env, line_id, fail_time):
        """Wait for a free crew, repair the line, restore service."""
        with self.repair_crew.request() as req:
            yield req
            duration = self.rng.uniform(self.cfg["repair_time_min"],
                                        self.cfg["repair_time_max"])
            self.crew_busy_hours += duration
            yield env.timeout(duration)

            self.line_status[line_id] = True
            self.recoveries += 1
            self.repair_times.append(env.now - fail_time)
            self.distribute_load()
            self.log(env, "RESTORE",
                     f"{line_id} restored after {env.now - fail_time:.2f} h "
                     f"(crew time {duration:.2f} h)")

    def line_monitor(self, env, line_id):
        """Per-line hourly check for overload and stochastic failure."""
        cap = LINE_CAPACITIES[line_id]
        while True:
            if self.line_status[line_id]:
                load = self.line_loads[line_id]
                frac = load / cap

                if frac > self.cfg["cascade_thresh"]:
                    self.cascade_events += 1
                    self.log(env, "CASCADE",
                             f"{line_id} OVERLOADED at {frac*100:.1f}% "
                             f"({load:.1f}/{cap} MW)")
                    fail_prob = min(self.cfg["base_fail_prob"]
                                    * self.cfg["overload_fail_mult"], 0.90)
                else:
                    fail_prob = self.cfg["base_fail_prob"]

                if self.rng.random() < fail_prob:
                    self.line_status[line_id] = False
                    self.failures += 1
                    self.fail_times.append(env.now)
                    self.log(env, "FAILURE",
                             f"{line_id} FAILED (load {load:.1f}/{cap} MW, "
                             f"{frac*100:.1f}%)")
                    self.distribute_load()

                    # Did the redistribution overload a neighbour? (cascade)
                    for other in LINE_CAPACITIES:
                        if other != line_id and self.line_status[other]:
                            of = self.line_loads[other] / LINE_CAPACITIES[other]
                            if of > self.cfg["cascade_thresh"]:
                                self.cascade_events += 1
                                self.log(env, "CASCADE",
                                         f"  -> {other} now {of*100:.1f}% "
                                         f"after redistribution")

                    env.process(self.repair_process(env, line_id, env.now))

            yield env.timeout(self.cfg["time_step"])

    def metrics_collector(self, env):
        """Sample state once per hour for the time-series outputs."""
        while True:
            self.ts["time"].append(env.now)
            self.ts["coal1"].append(self.gen_output["Coal Gen 1"])
            self.ts["coal2"].append(self.gen_output["Coal Gen 2"])
            self.ts["solar"].append(self.gen_output["Solar Farm"])
            self.ts["demand"].append(self.demand)

            active = [lid for lid, up in self.line_status.items() if up]
            if active:
                avg_pct = sum(self.line_loads[lid] / LINE_CAPACITIES[lid]
                              for lid in active) / len(active) * 100
            else:
                avg_pct = 0.0
            self.ts["load_pct"].append(avg_pct)
            self.ts["lines_up"].append(len(active))

            for lid in LINE_CAPACITIES:
                pct = (self.line_loads[lid] / LINE_CAPACITIES[lid] * 100
                       if self.line_status[lid] else 0.0)
                self.ts_line_pct[lid].append(pct)

            yield env.timeout(self.cfg["time_step"])

    # ------------------------------------------------------------------ #
    # Runner
    # ------------------------------------------------------------------ #
    def run(self):
        """Execute the simulation and return a results dictionary."""
        env = simpy.Environment()
        self.repair_crew = simpy.Resource(env, capacity=self.cfg["num_repair_crews"])

        env.process(self.generator_process(env))
        env.process(self.demand_process(env))
        env.process(self.metrics_collector(env))
        for lid in LINE_CAPACITIES:
            env.process(self.line_monitor(env, lid))

        # Prime the first hour so monitors see a sensible load.
        self.demand = TOTAL_CAPACITY * self.demand_fraction(0)
        self.distribute_load()

        t0 = wall_clock.perf_counter()
        env.run(until=self.cfg["sim_duration"])
        exec_ms = (wall_clock.perf_counter() - t0) * 1000.0

        mttr = (sum(self.repair_times) / len(self.repair_times)
                if self.repair_times else 0.0)
        peak_pct = max(self.ts["load_pct"]) if self.ts["load_pct"] else 0.0
        crew_util = (self.crew_busy_hours
                     / (self.cfg["num_repair_crews"] * self.cfg["sim_duration"]))

        return {
            "config": self.cfg,
            "exec_ms": exec_ms,
            "failures": self.failures,
            "recoveries": self.recoveries,
            "cascade_events": self.cascade_events,
            "mttr": mttr,
            "peak_load_pct": peak_pct,
            "crew_utilisation": crew_util,
            "unrecovered": self.failures - self.recoveries,
        }


def run_once(config=None, seed=None):
    """Convenience helper: build, run, and return (sim, results)."""
    sim = GridSimulation(config=config, seed=seed)
    results = sim.run()
    return sim, results
