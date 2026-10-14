"""Part A: read a rollout. TODO 1, 2 and 9 live here; the helpers below them are given."""
from __future__ import annotations

import numpy as np

from avsim import core

G = 9.81
HALF_EGO = core.CAR[0] / 2   # 2.3 m: half the ego's length


def ego_events(R: core.Rollout, k: int) -> list[dict]:
    """Failure events involving the ego in scenario k, earliest first (given).

    event["kind"] is "contact" (the boxes touched) or "block" (the ego's body stopped the pedestrian P1 on the
    crosswalk: pedestrians never walk into a car, so this is how a planner that stops too late fails them)."""
    return [e for e in R.events[k] if e["a"] == "ego" or e["b"] == "ego"]


def min_ttc(R: core.Rollout, cap: float = 10.0) -> np.ndarray:
    """TODO 1. (K,) smallest time-to-collision between the ego and whatever it is following, capped at `cap` s."""
    K, NF = R.F.shape[:2]
    ego_idx = core.IX["ego"]
    ego_F = R.F[:, :, ego_idx, :]
    x_ego = ego_F[..., 0]
    z_ego = ego_F[..., 1]
    hx_ego = ego_F[..., 2]
    hz_ego = ego_F[..., 3]
    v_ego = ego_F[..., 4]

    leader_idx = R.EGO[:, :, 3].astype(int)
    has_leader = (leader_idx >= 0)
    safe_leader = np.where(has_leader, leader_idx, 0)

    k_idx = np.arange(K)[:, None]
    f_idx = np.arange(NF)[None, :]
    leader_F = R.F[k_idx, f_idx, safe_leader, :]
    x_leader = leader_F[..., 0]
    z_leader = leader_F[..., 1]
    v_leader = leader_F[..., 4]

    half_len_all = np.where(core.PEDS, 0.3, core.LEN / 2.0)
    leader_half_len = half_len_all[safe_leader]

    rx = x_leader - x_ego
    rz = z_leader - z_ego
    lon = rx * hx_ego + rz * hz_ego
    gap = np.maximum(lon - 2.3 - leader_half_len, 0.0)
    dv = v_ego - v_leader

    valid = has_leader & (dv > 0.1)
    safe_dv = np.where(valid, dv, 1.0)
    ttc = np.where(valid, gap / safe_dv, np.inf)
    res = np.minimum(cap, ttc.min(axis=1))

    for k in range(K):
        if len(ego_events(R, k)) > 0:
            res[k] = 0.0
    return res


def contact_type(R: core.Rollout, k: int, event: dict) -> str:
    """TODO 2. 'front' (the ego ran into it), 'rear' (it ran into the ego) or 'side', at the contact frame."""
    f = event["f"]
    other_party = event["b"] if event["a"] == "ego" else event["a"]
    ego_idx = core.IX["ego"]
    other_idx = core.IX[other_party]

    ego_state = R.F[k, f, ego_idx]
    other_state = R.F[k, f, other_idx]

    rx = other_state[0] - ego_state[0]
    rz = other_state[1] - ego_state[1]
    hx = ego_state[2]
    hz = ego_state[3]

    lon = rx * hx + rz * hz
    lat = -rx * hz + rz * hx

    if lon > 2.3 and abs(lat) < 1.6:
        return "front"
    if lon < -2.3 and abs(lat) < 1.6:
        return "rear"
    return "side"


def progress_metrics(R: core.Rollout) -> tuple[np.ndarray, np.ndarray]:
    """TODO 9. Two (K,) arrays: the distance the ego covers in the 24 s (sum of frame-to-frame steps, metres),
    and the number of frames where the ego brakes harder than 3 m/s^2 (acceleration column < -3)."""
    e = R.F[:, :, core.IX["ego"]]
    dx = np.diff(e[..., 0], axis=1)
    dz = np.diff(e[..., 1], axis=1)
    dist = np.sum(np.hypot(dx, dz), axis=1)
    harsh = np.sum(e[..., 5] < -3.0, axis=1)
    return dist, harsh


# ---------------------------------------------------------------- given helpers

def pair_min_ttc(R, follower, leader, cap=10.0, lat_max=2.2, leader_vmin=-1.0):
    """(K,) smallest TTC of `follower` running into `leader` while they share a corridor."""
    F = R.F
    a, b = F[:, :, core.IX[follower]], F[:, :, core.IX[leader]]
    rx, rz = b[..., 0] - a[..., 0], b[..., 1] - a[..., 1]
    lon = rx * a[..., 2] + rz * a[..., 3]
    lat = -rx * a[..., 3] + rz * a[..., 2]
    gap = np.maximum(lon - core.LEN[core.IX[follower]] / 2 - core.LEN[core.IX[leader]] / 2, 0.0)
    dv = a[..., 4] - b[..., 4]
    ok = (lon > 0) & (np.abs(lat) < lat_max) & (dv > 0.1) & (b[..., 4] >= leader_vmin)
    ttc = np.where(ok, gap / np.maximum(dv, 1e-6), np.inf)
    return np.minimum(cap, ttc.min(1))


def ped_room(R, cap=30.0):
    """(K,) smallest stopping room [m] left while the crossing pedestrian is in the ego's lane
    (distance to them minus the ego's braking distance at mu*g). Negative = could not have stopped."""
    e, p = R.F[:, :, core.IX["ego"]], R.F[:, :, core.IX["P1"]]
    mu = np.asarray(R.params["mu"])[:, None]
    inlane = np.abs(p[..., 1] - e[..., 1]) < 1.9
    ahead = p[..., 0] - e[..., 0] - HALF_EGO
    room = np.where(inlane & (ahead > -1.0), ahead - e[..., 4] ** 2 / (2 * mu * G), cap)
    return np.clip(room.min(1), -cap, cap)
