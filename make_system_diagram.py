"""
make_system_diagram.py
Generates the conceptual system diagram for Task 2.1.

Draws the grid topology (generators -> lines -> substations -> consumer zones)
together with the simulation's control loop (monitor -> repair crew). Saves
system_diagram.png. Pure matplotlib so it runs anywhere, including Colab.

Module: Advanced Simulation Techniques (Task 2)
Author: Salina Khadka, BSBI Berlin
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def box(ax, x, y, w, h, text, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                linewidth=1.2, edgecolor="#444444",
                                facecolor=color))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=9, fontweight="bold", wrap=True)


def arrow(ax, x1, y1, x2, y2, style="-|>", color="#333333", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=14, linewidth=1.3,
                                 color=color, linestyle=ls,
                                 connectionstyle="arc3,rad=0.0"))


def main():
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")

    gen_c = "#cdd7f0"     # generators
    line_c = "#fde2b5"    # transmission
    sub_c = "#cfe9d4"     # substations
    zone_c = "#e7d4f0"    # consumer zones
    ctrl_c = "#f5c6c6"    # control / repair

    ax.text(6.5, 7.7, "Smart Grid Cascading-Failure Simulation — System Diagram",
            ha="center", fontsize=13, fontweight="bold")

    # Column headers
    for x, label in [(1.4, "GENERATION"), (4.2, "TRANSMISSION"),
                     (7.4, "SUBSTATIONS"), (10.6, "CONSUMER ZONES")]:
        ax.text(x, 7.1, label, ha="center", fontsize=9.5,
                fontweight="bold", color="#555555")

    # Generators
    gens = [("Coal Gen 1\n300 MW", 6.0), ("Coal Gen 2\n200 MW", 4.3),
            ("Solar Farm\n150 MW", 2.6)]
    for txt, y in gens:
        box(ax, 0.4, y, 2.0, 1.1, txt, gen_c)

    # Transmission lines
    lines = [("L1-A 250 MW", 6.0), ("L2-A 200 MW", 4.3),
             ("L3-B 180 MW", 2.6), ("L4-C 220 MW", 1.4),
             ("L5-D 160 MW", 0.2)]
    for txt, y in lines:
        box(ax, 3.3, y, 1.8, 0.75, txt, line_c)

    # Substations
    subs = [("Substation A", 6.0), ("Substation B", 4.0),
            ("Substation C", 2.2), ("Substation D", 0.5)]
    for txt, y in subs:
        box(ax, 6.5, y, 1.9, 0.9, txt, sub_c)

    # Consumer zones
    zones = [("Zone 1\nIndustrial (40%)", 6.0), ("Zone 2\nResidential (25%)", 4.0),
             ("Zone 3\nCommercial (20%)", 2.2), ("Zone 4\nMixed (15%)", 0.5)]
    for txt, y in zones:
        box(ax, 9.7, y, 2.0, 0.9, txt, zone_c)

    # Generation -> transmission
    arrow(ax, 2.4, 6.55, 3.3, 6.35)   # coal1 -> L1
    arrow(ax, 2.4, 4.85, 3.3, 4.65)   # coal2 -> L2
    arrow(ax, 2.4, 3.15, 3.3, 2.95)   # solar -> L3

    # Transmission -> substations
    arrow(ax, 5.1, 6.35, 6.5, 6.45)   # L1 -> A
    arrow(ax, 5.1, 4.65, 6.5, 6.2)    # L2 -> A
    arrow(ax, 5.1, 2.95, 6.5, 4.45)   # L3 -> B
    arrow(ax, 5.1, 1.75, 6.5, 2.65)   # L4 -> C
    arrow(ax, 5.1, 0.55, 6.5, 0.95)   # L5 -> D

    # Substations -> zones
    for ys, yz in [(6.45, 6.45), (4.45, 4.45), (2.65, 2.65), (0.95, 0.95)]:
        arrow(ax, 8.4, ys, 9.7, yz)

    # Control loop: repair crew (dashed feedback to failed lines)
    box(ax, 0.4, 0.1, 2.0, 0.9, "Repair Crew\n(SimPy Resource)", ctrl_c)
    arrow(ax, 3.3, 0.45, 2.4, 0.55, style="-|>", color="#c0392b", ls="--")
    ax.text(2.85, 0.15, "repair", color="#c0392b", fontsize=8, ha="center")

    # Boundary box (system boundary)
    ax.add_patch(plt.Rectangle((0.2, -0.2), 11.7, 7.0, fill=False,
                               linestyle="--", linewidth=1.3, edgecolor="#888888"))
    ax.text(0.3, 6.9, "System boundary", fontsize=8.5, color="#888888",
            style="italic")

    fig.tight_layout()
    fig.savefig("system_diagram.png", dpi=150, bbox_inches="tight")
    print("Saved: system_diagram.png")


if __name__ == "__main__":
    main()
