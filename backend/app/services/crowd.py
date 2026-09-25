"""
Crowd risk detection and operational actions.

Risk is computed from measured/estimated crowd occupancy against stated
capacity. The system only *recommends* actions; every decision requires
authority confirmation before it reaches the public channel.
"""


def crowd_level(occupancy_ratio: float) -> str:
    if occupancy_ratio < 0.45:
        return "low"
    if occupancy_ratio < 0.70:
        return "moderate"
    if occupancy_ratio < 0.90:
        return "high"
    return "critical"


def risk_label(level: str, expected_ratio: float = 0.0) -> str:
    if level == "critical" or expected_ratio > 1.0:
        return "HIGH CROWD RISK"
    if level == "high":
        return "MODERATE CROWD RISK"
    if level == "moderate":
        return "ELEVATED ACTIVITY"
    return "NORMAL"


def suggested_actions(level: str, capacity: int, current: int, expected: int, festival: bool = False) -> list:
    actions = []
    overdue_expected = expected >= capacity * 0.85
    if level in ("high", "critical") or overdue_expected:
        actions.append({"action": "Open additional parking", "detail": "Activate temporary parking zones near the venue."})
        actions.append({"action": "Increase shuttle services", "detail": "Add shuttle frequency between parking and the attraction."})
        actions.append({"action": "Deploy additional personnel", "detail": "Station crowd-management staff at entry and choke points."})
        actions.append({"action": "Open alternate entry/exit routes", "detail": "Relieve the main gate to reduce queue pressure."})
        actions.append({"action": "Promote nearby attractions", "detail": "Redirect visitors toward cultural alternatives with free capacity."})
        actions.append({"action": "Increase medical readiness", "detail": "Keep first-aid stations and ambulances on standby."})
        actions.append({"action": "Notify nearby hotels", "detail": "Advise accommodation partners about arrival-density peaks."})
        actions.append({"action": "Issue public alerts", "detail": "Publish a crowd advisory to the tourist application."})
    if level == "moderate":
        actions.append({"action": "Monitor entry flow", "detail": "Track gate-wise inflow and hold entry if 85% occupancy is reached."})
        actions.append({"action": "Prepare call-in staff", "detail": "Keep an on-call crowd team ready within 20 minutes."})
    if level == "low":
        actions.append({"action": "Routine observation", "detail": "No escalation required at this time."})
    return actions


def assess(capacity: int, current_visitors: int, expected_visitors: int) -> dict:
    ratio = current_visitors / capacity if capacity else 0.0
    level = crowd_level(ratio)
    return {
        "level": level,
        "occupancy_ratio": round(ratio, 3),
        "risk": risk_label(level, expected_visitors / capacity if capacity else 0.0),
        "actions": suggested_actions(level, capacity, current_visitors, expected_visitors, festival=True),
    }