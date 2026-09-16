from typing import List, Optional
from pydantic import BaseModel, Field


class OptimizationShipmentInput(BaseModel):
    """One ML-scored shipment plus the business context required by PuLP."""

    shipment_id: str
    late_probability: float = Field(ge=0.0, le=1.0)
    late_penalty: float = Field(ge=0.0)

    baseline_time_days: Optional[float] = Field(
        default=None,
        ge=0.0,
    )

    expedite_available: bool = True
    priority_available: bool = True
    route_available: bool = True
    hub_available: bool = True


class OptimizationConstraints(BaseModel):
    total_budget: float = Field(default=10000.0, ge=0.0)
    expedite_capacity: int = Field(default=1, ge=0)
    priority_capacity: int = Field(default=1, ge=0)
    route_capacity: int = Field(default=1, ge=0)
    hub_capacity: int = Field(default=1, ge=0)


class OptimizeRequest(BaseModel):
    shipments: List[OptimizationShipmentInput]
    constraints: OptimizationConstraints = Field(default_factory=OptimizationConstraints)
    request_id: Optional[str] = None
    # DB prediction IDs corresponding to shipments.
    # If supplied, optimizer recommendations are persisted.
    prediction_ids: Optional[List[Optional[int]]] = None


class RecommendationItem(BaseModel):
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


class OptimizeResponse(BaseModel):
    request_id: Optional[str] = None
    optimization_status: str
    total_intervention_cost: float
    total_expected_saving: float
    recommendations: List[RecommendationItem]

    # Present only when recommendations are persisted
    recommendation_ids: Optional[List[Optional[int]]] = None
