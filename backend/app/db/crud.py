from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    Decision,
    Outcome,
    Prediction,
    Recommendation,
    Shipment,
)


# ============================================================
# INSERTS
# ============================================================

def insert_shipment(
    db: Session,
    shipment_data: dict,
) -> Shipment:

    shipment = Shipment(**shipment_data)

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    return shipment


def insert_prediction(
    db: Session,
    shipment_id: int,
    risk_probability: float,
    predicted_class: str,
    model_version: str,
    eligibility_status: str = "eligible",
) -> Prediction:

    prediction = Prediction(
        shipment_id=shipment_id,
        risk_probability=risk_probability,
        predicted_class=predicted_class,
        model_version=model_version,
        eligibility_status=eligibility_status,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


def insert_recommendations(
    db: Session,
    prediction_id: int,
    recommendations: list[dict],
) -> list[Recommendation]:

    rows = [
        Recommendation(
            prediction_id=prediction_id,
            **recommendation,
        )
        for recommendation in recommendations
    ]

    db.add_all(rows)
    db.commit()

    for row in rows:
        db.refresh(row)

    return rows


def execute_decision(
    db: Session,
    recommendation_id: int,
    shipment_id: int,
    executed_by: str,
    predicted_cost_at_exec: float,
    predicted_time_at_exec: float,
) -> Decision:

    decision = Decision(
        recommendation_id=recommendation_id,
        shipment_id=shipment_id,
        executed_by=executed_by,
        status="executed",
        predicted_cost_at_exec=predicted_cost_at_exec,
        predicted_time_at_exec=predicted_time_at_exec,
    )

    try:
        db.add(decision)
        db.commit()
        db.refresh(decision)

        return decision

    except Exception:
        db.rollback()
        raise


def insert_outcome(
    db: Session,
    decision_id: int,
    actual_cost: float,
    actual_time_days: float,
    actual_delayed: bool,
) -> Outcome:

    outcome = Outcome(
        decision_id=decision_id,
        actual_cost=actual_cost,
        actual_time_days=actual_time_days,
        actual_delayed=actual_delayed,
    )

    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    return outcome


# ============================================================
# RETRIEVALS
# ============================================================

def get_shipment(
    db: Session,
    shipment_id: int,
) -> Shipment | None:

    return db.get(
        Shipment,
        shipment_id,
    )


def get_latest_prediction(
    db: Session,
    shipment_id: int,
) -> Prediction | None:

    stmt = (
        select(Prediction)
        .where(
            Prediction.shipment_id == shipment_id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .limit(1)
    )

    return db.execute(
        stmt
    ).scalar_one_or_none()


def get_recommendations_for_prediction(
    db: Session,
    prediction_id: int,
) -> list[Recommendation]:

    stmt = (
        select(Recommendation)
        .where(
            Recommendation.prediction_id
            == prediction_id
        )
        .order_by(
            Recommendation.rank.asc()
        )
    )

    return list(
        db.execute(stmt).scalars()
    )


def get_decision_history(
    db: Session,
    shipment_id: int | None = None,
) -> list[Decision]:

    stmt = select(
        Decision
    ).order_by(
        Decision.executed_at.desc()
    )

    if shipment_id is not None:
        stmt = stmt.where(
            Decision.shipment_id == shipment_id
        )

    return list(
        db.execute(stmt).scalars()
    )


def get_decision_roi(
    db: Session,
    decision_id: int,
) -> dict | None:

    decision = db.get(
        Decision,
        decision_id,
    )

    if decision is None:
        return None

    outcome = decision.outcome

    if outcome is None:
        return {
            "decision_id": decision_id,
            "status": "outcome_pending",
        }

    predicted_cost = float(
        decision.predicted_cost_at_exec
    )

    actual_cost = (
        float(outcome.actual_cost)
        if outcome.actual_cost is not None
        else None
    )

    predicted_time = float(
        decision.predicted_time_at_exec
    )

    actual_time = (
        float(outcome.actual_time_days)
        if outcome.actual_time_days is not None
        else None
    )

    return {
        "decision_id": decision_id,
        "shipment_id": decision.shipment_id,

        "predicted_cost": predicted_cost,
        "actual_cost": actual_cost,

        "cost_savings": (
            predicted_cost - actual_cost
            if actual_cost is not None
            else None
        ),

        "predicted_time_days": predicted_time,
        "actual_time_days": actual_time,

        "actual_delayed": outcome.actual_delayed,
    }


def get_all_roi(
    db: Session,
) -> list[dict]:

    stmt = select(Decision)

    decisions = db.execute(
        stmt
    ).scalars()

    results = []

    for decision in decisions:

        roi = get_decision_roi(
            db,
            decision.decision_id,
        )

        if roi:
            results.append(roi)

    return results