from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud

from datetime import datetime


router = APIRouter(
    prefix="/api/v1",
    tags=["write-back"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class ExecuteDecisionRequest(BaseModel):
    recommendation_id: int
    shipment_id: int
    executed_by: str
    predicted_cost_at_exec: float
    predicted_time_at_exec: float


class OutcomeRequest(BaseModel):
    decision_id: int
    actual_cost: float
    actual_time_days: float
    actual_delayed: bool

class ShipmentRequest(BaseModel):
    origin: str
    destination: str
    carrier: str | None = None
    product_type: str | None = None
    quantity: float | None = None
    scheduled_ship_date: datetime | None = None
    scheduled_delivery_date: datetime | None = None


# ============================================================
# ROUTES
# ============================================================
@router.post("/shipments")
def create_shipment(
    payload: ShipmentRequest,
    db: Session = Depends(get_db),
):
    shipment = crud.insert_shipment(
        db,
        payload.model_dump(),
    )

    return {
        "shipment_id": shipment.shipment_id,
        "origin": shipment.origin,
        "destination": shipment.destination,
    }

@router.post("/decisions/execute")
def execute_decision(
    payload: ExecuteDecisionRequest,
    db: Session = Depends(get_db),
):
    decision = crud.execute_decision(
        db,
        recommendation_id=payload.recommendation_id,
        shipment_id=payload.shipment_id,
        executed_by=payload.executed_by,
        predicted_cost_at_exec=payload.predicted_cost_at_exec,
        predicted_time_at_exec=payload.predicted_time_at_exec,
    )

    return {
        "decision_id": decision.decision_id,
        "status": decision.status,
    }


@router.get("/decisions/history")
def decision_history(
    shipment_id: int | None = None,
    db: Session = Depends(get_db),
):
    decisions = crud.get_decision_history(
        db,
        shipment_id=shipment_id,
    )

    return [
        {
            "decision_id": d.decision_id,
            "shipment_id": d.shipment_id,
            "status": d.status,
            "executed_by": d.executed_by,
            "executed_at": d.executed_at,
            "predicted_cost_at_exec": float(
                d.predicted_cost_at_exec
            ),
            "predicted_time_at_exec": float(
                d.predicted_time_at_exec
            ),
        }
        for d in decisions
    ]


@router.post("/outcomes")
def record_outcome(
    payload: OutcomeRequest,
    db: Session = Depends(get_db),
):
    outcome = crud.insert_outcome(
        db,
        decision_id=payload.decision_id,
        actual_cost=payload.actual_cost,
        actual_time_days=payload.actual_time_days,
        actual_delayed=payload.actual_delayed,
    )

    return {
        "outcome_id": outcome.outcome_id
    }


@router.get("/decisions/{decision_id}/roi")
def decision_roi(
    decision_id: int,
    db: Session = Depends(get_db),
):
    roi = crud.get_decision_roi(
        db,
        decision_id,
    )

    if roi is None:
        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    return roi


@router.get("/roi")
def all_roi(
    db: Session = Depends(get_db),
):
    return crud.get_all_roi(db)