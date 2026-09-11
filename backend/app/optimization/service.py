from pathlib import Path
from typing import List

import pandas as pd
import pulp

from app.api.schemas.optimization import (
    OptimizationShipmentInput,
    OptimizationConstraints,
    RecommendationItem,
)
from app.optimization.optimizer import optimize_shipments


class OptimizationService:
    def __init__(self, intervention_file: str | Path | None = None):
        if intervention_file is None:
            intervention_file = Path(__file__).resolve().parent / "data" / "interventions.csv"
        self.intervention_file = Path(intervention_file)

    def optimize(
        self,
        shipments: List[OptimizationShipmentInput],
        constraints: OptimizationConstraints,
    ) -> tuple[str, list[RecommendationItem], float, float]:
        if not shipments:
            raise ValueError("At least one shipment is required for optimization.")

        df = pd.DataFrame([shipment.model_dump() for shipment in shipments])

        model, result_df = optimize_shipments(
            shipments=df,
            intervention_file=str(self.intervention_file),
            total_budget=constraints.total_budget,
            expedite_capacity=constraints.expedite_capacity,
            priority_capacity=constraints.priority_capacity,
            route_capacity=constraints.route_capacity,
            hub_capacity=constraints.hub_capacity,
        )

        status = pulp.LpStatus[model.status]
        if status not in {"Optimal", "Feasible"}:
            return status, [], 0.0, 0.0

        recommendations = [
            RecommendationItem(
                shipment_id=str(row["shipment_id"]),
		action_id=str(row["action_id"]),
                selected_action=str(row["selected_action"]),
                late_probability=float(row["late_probability"]),
                risk_after=float(row["risk_after"]),
                action_cost=float(row["action_cost"]),
                baseline_expected_loss=float(row["baseline_expected_loss"]),
                optimized_expected_cost=float(row["optimized_expected_cost"]),
                expected_saving=float(row["expected_saving"]),
                predicted_time_days=(
                    float(row["predicted_time_days"])
                    if pd.notna(row["predicted_time_days"])
                    else None
                ),
            )
            for _, row in result_df.iterrows()
        ]

        total_cost = float(result_df["action_cost"].sum()) if not result_df.empty else 0.0
        total_saving = float(result_df["expected_saving"].sum()) if not result_df.empty else 0.0

        return status, recommendations, total_cost, total_saving


_optimization_service: OptimizationService | None = None


def get_optimization_service() -> OptimizationService:
    global _optimization_service
    if _optimization_service is None:
        _optimization_service = OptimizationService()
    return _optimization_service
