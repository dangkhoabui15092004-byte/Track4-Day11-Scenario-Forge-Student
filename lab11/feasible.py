"""Part B: physics check. TODO 3."""
from __future__ import annotations

import math

G = 9.81


def is_feasible(p: dict) -> bool:
    """TODO 3. False for scenarios no real road user could produce."""
    mu = p["mu"]
    max_acc = mu * G

    # 1. Cosine lane change lateral acceleration
    cut_dur = p["cutDur"]
    a_lat = (math.pi / cut_dur) ** 2 * 3.5 / 2.0
    if a_lat > max_acc:
        return False

    # 2. Post-merge braking
    if p["cutBrake"] > max_acc:
        return False

    # 3. Pedestrian speed
    if p["pedV"] > 2.5:
        return False

    # 4. Cut-in speed
    if not (0 < p["cutV"] <= 22):
        return False

    return True
