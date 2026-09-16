import pandas as pd
import pulp
from .validation import validate_optimization_input

def optimize_shipments(
    shipments: pd.DataFrame,
    intervention_file: str,
    total_budget: float,
    expedite_capacity: int,
    priority_capacity: int,
    route_capacity: int,
    hub_capacity: int
):
    shipments = shipments.copy()
    
    validate_optimization_input(
        shipments
    )
    
    interventions = pd.read_csv(intervention_file)
    

    # Only enabled interventions
    interventions = interventions[
        interventions["enabled"] == 1
    ].copy()

    # ----------------------------------------
    # CREATE OPTIMIZATION MODEL
    # ----------------------------------------

    model = pulp.LpProblem(
        "SupplyPrescript_Optimization",
        pulp.LpMinimize
    )

    # ----------------------------------------
    # DECISION VARIABLES
    # x[(shipment, action)] = 1 if selected
    # ----------------------------------------

    x = {}

    for _, shipment in shipments.iterrows():
        shipment_id = shipment["shipment_id"]

        for _, action in interventions.iterrows():
            action_id = action["action_id"]

            x[(shipment_id, action_id)] = pulp.LpVariable(
                f"x_{shipment_id}_{action_id}",
                cat="Binary"
            )

    # ----------------------------------------
    # CALCULATE EXPECTED COSTS
    # ----------------------------------------

    expected_cost = {}

    for _, shipment in shipments.iterrows():

        shipment_id = shipment["shipment_id"]
        probability = shipment["late_probability"]
        penalty = shipment["late_penalty"]

        for _, action in interventions.iterrows():

            action_id = action["action_id"]

            action_cost = action["base_cost"]
            risk_reduction = action["risk_reduction"]

            risk_after = probability * (
                1 - risk_reduction
            )

            total_expected_cost = (
                action_cost
                +
                risk_after * penalty
            )

            expected_cost[
                (shipment_id, action_id)
            ] = total_expected_cost

    # ----------------------------------------
    # OBJECTIVE
    # Minimize total expected business cost
    # ----------------------------------------

    model += pulp.lpSum(
        expected_cost[(shipment_id, action_id)]
        *
        x[(shipment_id, action_id)]

        for shipment_id, action_id in x
    )

    # ----------------------------------------
    # CONSTRAINT 1
    # Exactly one action per shipment
    # ----------------------------------------

    for _, shipment in shipments.iterrows():

        shipment_id = shipment["shipment_id"]

        model += (
            pulp.lpSum(
                x[(shipment_id, action["action_id"])]
                for _, action in interventions.iterrows()
            )
            == 1
        )

    # ----------------------------------------
    # CONSTRAINT 2
    # Total intervention budget
    # ----------------------------------------

    model += (
        pulp.lpSum(
            action["base_cost"]
            *
            x[(shipment["shipment_id"], action["action_id"])]

            for _, shipment in shipments.iterrows()
            for _, action in interventions.iterrows()
        )
        <= total_budget
    )

    # ----------------------------------------
    # CONSTRAINT 3
    # Intervention capacities
    # ----------------------------------------

    action_capacities = {
        "A1": expedite_capacity,
        "A2": priority_capacity,
        "A3": route_capacity,
        "A4": hub_capacity,
    }

    for action_id, capacity in action_capacities.items():

        model += (
            pulp.lpSum(
                x[(shipment["shipment_id"], action_id)]
                for _, shipment in shipments.iterrows()
            )
            <= capacity
        )
    # ----------------------------------------
    # CONSTRAINT 4
    # Shipment-specific feasibility
    # ----------------------------------------

    availability_columns = {
        "A1": "expedite_available",
        "A2": "priority_available",
        "A3": "route_available",
        "A4": "hub_available"
    }

    for _, shipment in shipments.iterrows():

        shipment_id = shipment["shipment_id"]

        for action_id, availability_column in availability_columns.items():

            available = int(shipment[availability_column])

            model += (
                x[(shipment_id, action_id)]
                <= available
            )

    # ----------------------------------------
    # SOLVE
    # ----------------------------------------

    model.solve(
        pulp.PULP_CBC_CMD(msg=False)
    )

    # ----------------------------------------
    # COLLECT RESULTS
    # ----------------------------------------

    results = []

    for _, shipment in shipments.iterrows():

        shipment_id = shipment["shipment_id"]
        probability = shipment["late_probability"]
        penalty = shipment["late_penalty"]

        baseline_loss = probability * penalty

        for _, action in interventions.iterrows():

            action_id = action["action_id"]

            if pulp.value(
                x[(shipment_id, action_id)]
            ) == 1:

                cost = action["base_cost"]
                reduction = action["risk_reduction"]
                time_reduction = float(
                    action["time_reduction_days"]
                )

                baseline_time = shipment.get(
                    "baseline_time_days"
                )

                if pd.notna(baseline_time):
                    predicted_time_days = max(
                        0.0,
                        float(baseline_time)
                        - time_reduction
                    )
                else:
                    predicted_time_days = None

                risk_after = probability * (
                    1 - reduction
                )

                optimized_cost = (
                    cost
                    +
                    risk_after * penalty
                )

                saving = (
                    baseline_loss
                    -
                    optimized_cost
                )

                results.append({
                    "shipment_id": shipment_id,
                    "action_id": action_id,
                    "selected_action": action["action_name"],
                    "late_probability": probability,
                    "risk_after": risk_after,
                    "action_cost": cost,
                    "baseline_expected_loss": baseline_loss,
                    "optimized_expected_cost": optimized_cost,
                    "expected_saving": saving,
                    "predicted_time_days": predicted_time_days,
                })
    result_df = pd.DataFrame(results)

    return (
        model,
        result_df
    )
