import pandas as pd

from .feasibility import check_action_feasibility

from .cost_model import (
    calculate_baseline_expected_loss,
    calculate_risk_after_action,
    calculate_expected_cost_after_action,
    calculate_expected_saving,
)


def evaluate_interventions(
    late_probability: float,
    late_penalty: float,
    intervention_file: str,
    available_budget: float,
    expedite_available: bool = True,
    priority_available: bool = True,
    alternative_route_available: bool = True,
    alternative_hub_available: bool = True,
):
    interventions = pd.read_csv(intervention_file)

    baseline_loss = calculate_baseline_expected_loss(late_probability, late_penalty)

    results = []

    for _, action in interventions.iterrows():

        feasible, reason = check_action_feasibility(
            action_name=action["action_name"],
            action_cost=action["base_cost"],
            available_budget=available_budget,
            expedite_available=expedite_available,
            priority_available=priority_available,
            alternative_route_available=alternative_route_available,
            alternative_hub_available=alternative_hub_available,
        )

        if action["enabled"] != 1:
            continue

        risk_after = calculate_risk_after_action(
            late_probability, action["risk_reduction"]
        )

        expected_cost = calculate_expected_cost_after_action(
            action["base_cost"], risk_after, late_penalty
        )

        expected_saving = calculate_expected_saving(baseline_loss, expected_cost)

        results.append(
            {
                "action_id": action["action_id"],
                "action_name": action["action_name"],
                "action_cost": action["base_cost"],
                "risk_before": late_probability,
                "risk_after": risk_after,
                "baseline_expected_loss": baseline_loss,
                "expected_cost": expected_cost,
                "expected_saving": expected_saving,
                "feasible": feasible,
                "reason": reason,
            }
        )

    result_df = pd.DataFrame(results)

    feasible_df = result_df[
        (result_df["feasible"] == True)
        &
        (
            (result_df["action_name"] == "NO_ACTION")
            |
            (result_df["expected_saving"] > 0)
        )
    ].copy()


    feasible_df = feasible_df.sort_values(
        by=["expected_saving", "action_cost", "risk_after"], ascending=[False, True, True]
    ).reset_index(drop=True)

    feasible_df["rank"] = feasible_df.index + 1

    return feasible_df
