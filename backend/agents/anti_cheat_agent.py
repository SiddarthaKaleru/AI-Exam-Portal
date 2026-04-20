"""Agent 6 — Anti-Cheating Agent.

Processes client-side anti-cheat events and flags suspicious behavior.
"""


def anti_cheat_agent(events: list) -> dict:
    """Analyze anti-cheat events from the frontend.

    Args:
        events: List of event dicts from the client, e.g.:
            [{"type": "tab_switch", "timestamp": "..."}, ...]

    Returns:
        dict with flags, severity, and summary.
    """
    print("🛡️  Agent 6: Anti-Cheat — analyzing behavior...")

    tab_switches = 0
    copy_pastes = 0
    focus_losses = 0
    right_clicks = 0
    flags = []

    for event in events:
        event_type = event.get("type", "")
        if event_type == "tab_switch":
            tab_switches += 1
        elif event_type == "copy_paste":
            copy_pastes += 1
        elif event_type == "focus_loss":
            focus_losses += 1
        elif event_type == "right_click":
            right_clicks += 1

    # Flagging rules
    if tab_switches >= 3:
        flags.append({
            "type": "tab_switch",
            "count": tab_switches,
            "severity": "high" if tab_switches >= 5 else "medium",
            "message": f"Student switched tabs {tab_switches} times",
        })

    if copy_pastes >= 1:
        flags.append({
            "type": "copy_paste",
            "count": copy_pastes,
            "severity": "high",
            "message": f"Copy/paste detected {copy_pastes} times",
        })

    if focus_losses >= 5:
        flags.append({
            "type": "focus_loss",
            "count": focus_losses,
            "severity": "medium",
            "message": f"Window lost focus {focus_losses} times",
        })

    # Overall severity
    if any(f["severity"] == "high" for f in flags):
        severity = "high"
    elif flags:
        severity = "medium"
    else:
        severity = "clean"

    result = {
        "flags": flags,
        "severity": severity,
        "summary": {
            "tab_switches": tab_switches,
            "copy_pastes": copy_pastes,
            "focus_losses": focus_losses,
            "right_clicks": right_clicks,
            "total_events": len(events),
        },
        "is_suspicious": severity in ("high", "medium"),
    }

    print(f"   ✅ Anti-cheat: severity={severity}, {len(flags)} flags")
    return result
