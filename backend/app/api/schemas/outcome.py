from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OptimizationOutcomeRequest(BaseModel):
    actual_intervention_cost: float = Field(ge=0.0)
    actual_time_days: float = Field(ge=0.0)
    actual_delayed: bool
    actual_delay_cost: float = Field(
        default=0.0,
        ge=0.0,
    )
    outcome_note: Optional[str] = None


class OptimizationOutcomeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    outcome_id: int
    decision_id: int

    actual_intervention_cost: float
    actual_time_days: float
    actual_delayed: bool
    actual_delay_cost: float

    actual_total_cost: float

    outcome_note: Optional[str] = None

    recorded_at: datetime

class OutcomeROIResponse(BaseModel):
    decision_id: int
    recommendation_id: int
    outcome_id: int

    selected_action: str

    # Predicted / optimized values
    baseline_expected_loss: float
    predicted_action_cost: float
    optimized_expected_cost: float
    predicted_expected_saving: float
    predicted_time_days: Optional[float] = None

    # Actual values
    actual_intervention_cost: float
    actual_delay_cost: float
    actual_total_cost: float
    actual_time_days: float
    actual_delayed: bool

    # Comparison metrics
    intervention_cost_variance: float
    optimized_cost_variance: float
    realized_savings_vs_baseline: float
    savings_variance: float

    time_variance_days: Optional[float] = None
    realized_roi_percent: Optional[float] = None
