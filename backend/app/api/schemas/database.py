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