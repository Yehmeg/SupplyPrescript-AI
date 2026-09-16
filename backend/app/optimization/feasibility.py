def check_action_feasibility(
    action_name: str,
    action_cost: float,
    available_budget: float,
    expedite_available: bool = True,
    priority_available: bool = True,
    alternative_route_available: bool = True,
    alternative_hub_available: bool = True
):
    # NO_ACTION is always feasible
    if action_name == "NO_ACTION":
        return True, "Always feasible"

    # Budget constraint
    if action_cost > available_budget:
        return False, "Action cost exceeds available budget"

    # Operational availability constraints
    if action_name == "EXPEDITE" and not expedite_available:
        return False, "Expedite service unavailable"

    if action_name == "PRIORITY_HANDLING" and not priority_available:
        return False, "Priority handling unavailable"

    if action_name == "ALTERNATIVE_ROUTE" and not alternative_route_available:
        return False, "Alternative route unavailable"

    if action_name == "ALTERNATIVE_HUB" and not alternative_hub_available:
        return False, "Alternative hub unavailable"

    return True, "Feasible"