from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class RecommendationDecisionRequest(BaseModel):
    decision_status: Literal[
        "ACCEPTED",
        "REJECTED",
    ]

    decided_by: Optional[str] = None
    decision_note: Optional[str] = None


class RecommendationDecisionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    decision_id: int
    recommendation_id: int

    decision_status: str
    execution_status: str

    decided_by: Optional[str] = None
    decision_note: Optional[str] = None

    decided_at: datetime
    executed_at: Optional[datetime] = None