"""Part D: name the failure. TODO 8."""
from __future__ import annotations

from avsim import core


def label_mode(R: core.Rollout, k: int, event: dict, contact_type) -> str:
    """TODO 8. Name the kind of failure behind one ego failure event (a collision, or a crosswalk block)."""
    other_party = event["b"] if event["a"] == "ego" else event["a"]

    # 1. crosswalk_block
    if other_party == "P1" or event.get("kind") == "block":
        return "crosswalk_block"

    # 2. rear_ended
    if contact_type(R, k, event) == "rear":
        return "rear_ended"

    # 3. bus_bypass or cut_in
    if other_party == "C2":
        f = event["f"]
        c2_state = R.F[k, f, core.IX["C2"]]
        x_c2 = c2_state[0]
        v_c2 = c2_state[4]
        if x_c2 < 112.0 and v_c2 < 6.0:
            return "bus_bypass"
        return "cut_in"

    return "other"
