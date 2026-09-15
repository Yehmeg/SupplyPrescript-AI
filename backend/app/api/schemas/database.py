from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PredictionDBResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prediction_id: int
    order_id: int

    model_version: str

    late_risk_probability: float
    predicted_late_risk: bool

    prediction_eligible: bool
    exclusion_reason: Optional[str] = None

    threshold_used: float

    ensemble_models_used: Optional[list[str]] = None

    created_at: datetime

    request_id: Optional[str] = None


class OrderDBResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int

    order_status: Optional[str] = None

    source_system: Optional[str] = None

    received_at: datetime


class OrderWithPredictionsResponse(BaseModel):
    order: OrderDBResponse
    predictions: list[PredictionDBResponse]

class OptimizationRunDBResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    run_id: int
    request_id: Optional[str] = None

    optimization_status: str

    total_intervention_cost: float
    total_expected_saving: float

    created_at: datetime


class OptimizationRecommendationDBResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: int
    run_id: int

    prediction_id: Optional[int] = None

    shipment_id: str

    action_id: str
    selected_action: str

    late_probability: float
    risk_after: float

    action_cost: float
    baseline_expected_loss: float
    optimized_expected_cost: float
    expected_saving: float

    predicted_time_days: Optional[float] = None

    created_at: datetime


class OptimizationRunWithRecommendationsResponse(BaseModel):
    run: OptimizationRunDBResponse
    recommendations: list[
        OptimizationRecommendationDBResponse
    ]