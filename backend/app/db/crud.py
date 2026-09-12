from typing import Any, Optional

from sqlalchemy.orm import Session

from app.db.models import (
    MLPrediction,
    OptimizationRecommendation,
    OptimizationRun,
    Order,
    RecommendationDecision,
)

from sqlalchemy import func


# Maps the ML/API feature names to Python ORM attribute names.
ORDER_FIELD_MAP = {
    "Type": "order_type",
    "Days for shipment (scheduled)": "days_for_shipment_scheduled",
    "Benefit per order": "benefit_per_order",
    "Sales per customer": "sales_per_customer",
    "Category Name": "category_name",
    "Customer City": "customer_city",
    "Customer Country": "customer_country",
    "Customer Segment": "customer_segment",
    "Customer State": "customer_state",
    "Department Name": "department_name",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Market": "market",
    "Order City": "order_city",
    "Order Country": "order_country",
    "Order Item Discount": "order_item_discount",
    "Order Item Discount Rate": "order_item_discount_rate",
    "Order Item Product Price": "order_item_product_price",
    "Order Item Profit Ratio": "order_item_profit_ratio",
    "Order Item Quantity": "order_item_quantity",
    "Sales": "sales",
    "Order Item Total": "order_item_total",
    "Order Profit Per Order": "order_profit_per_order",
    "Order Region": "order_region",
    "Order State": "order_state",
    "Product Category Id": "product_category_id",
    "Product Name": "product_name",
    "Product Price": "product_price",
    "Order_Year": "order_year",
    "Order_Month": "order_month",
    "Order_DayOfWeek": "order_day_of_week",
    "Order_Day": "order_day",
}


def insert_order(
    db: Session,
    payload: dict[str, Any],
    source_system: str = "api",
) -> Order:
    """
    Insert one incoming order into the orders table.
    """

    order_values = {}

    for source_name, model_name in ORDER_FIELD_MAP.items():
        if source_name in payload:
            order_values[model_name] = payload[source_name]

    # Support either naming convention.
    if "order_status" in payload:
        order_values["order_status"] = payload["order_status"]
    elif "Order Status" in payload:
        order_values["order_status"] = payload["Order Status"]

    order_values["source_system"] = source_system

    # Keep the original request for auditing/debugging.
    order_values["raw_payload"] = payload

    order = Order(**order_values)

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def insert_ml_prediction(
    db: Session,
    *,
    order_id: int,
    model_version: str,
    late_risk_probability: float,
    predicted_late_risk: bool,
    prediction_eligible: bool,
    threshold_used: float,
    ensemble_models_used: Optional[list[str]] = None,
    exclusion_reason: Optional[str] = None,
    request_id: Optional[str] = None,
) -> MLPrediction:
    """
    Store one ML prediction linked to an existing order.
    """

    prediction = MLPrediction(
        order_id=order_id,
        model_version=model_version,
        late_risk_probability=late_risk_probability,
        predicted_late_risk=predicted_late_risk,
        prediction_eligible=prediction_eligible,
        exclusion_reason=exclusion_reason,
        threshold_used=threshold_used,
        ensemble_models_used=ensemble_models_used,
        request_id=request_id,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


def get_order(
    db: Session,
    order_id: int,
) -> Optional[Order]:
    return (
        db.query(Order)
        .filter(Order.order_id == order_id)
        .first()
    )


def get_prediction(
    db: Session,
    prediction_id: int,
) -> Optional[MLPrediction]:
    return (
        db.query(MLPrediction)
        .filter(
            MLPrediction.prediction_id == prediction_id
        )
        .first()
    )


def get_predictions_for_order(
    db: Session,
    order_id: int,
) -> list[MLPrediction]:
    return (
        db.query(MLPrediction)
        .filter(MLPrediction.order_id == order_id)
        .order_by(MLPrediction.created_at.desc())
        .all()
    )


def get_latest_prediction(
    db: Session,
    order_id: int,
) -> Optional[MLPrediction]:
    return (
        db.query(MLPrediction)
        .filter(MLPrediction.order_id == order_id)
        .order_by(MLPrediction.created_at.desc())
        .first()
    )

def insert_optimization_run(
    db: Session,
    *,
    request_id: Optional[str],
    optimization_status: str,
    total_intervention_cost: float,
    total_expected_saving: float,
) -> OptimizationRun:

    run = OptimizationRun(
        request_id=request_id,
        optimization_status=optimization_status,
        total_intervention_cost=total_intervention_cost,
        total_expected_saving=total_expected_saving,
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


def insert_optimization_recommendations(
    db: Session,
    *,
    run_id: int,
    prediction_ids: list[Optional[int]],
    recommendations: list[Any],
) -> list[OptimizationRecommendation]:

    if len(prediction_ids) != len(recommendations):
        raise ValueError(
            "prediction_ids count must match recommendations count"
        )

    rows = []

    for prediction_id, recommendation in zip(
        prediction_ids,
        recommendations,
    ):
        # Support either Pydantic objects or dictionaries.
        if hasattr(recommendation, "model_dump"):
            data = recommendation.model_dump()
        else:
            data = dict(recommendation)

        row = OptimizationRecommendation(
            run_id=run_id,
            prediction_id=prediction_id,
            shipment_id=data["shipment_id"],
            action_id=data["action_id"],
            selected_action=data["selected_action"],
            late_probability=data["late_probability"],
            risk_after=data["risk_after"],
            action_cost=data["action_cost"],
            baseline_expected_loss=data[
                "baseline_expected_loss"
            ],
            optimized_expected_cost=data[
                "optimized_expected_cost"
            ],
            expected_saving=data["expected_saving"],
            predicted_time_days=data.get(
                "predicted_time_days"
            ),
        )

        db.add(row)
        rows.append(row)

    db.commit()

    for row in rows:
        db.refresh(row)

    return rows


def get_optimization_run(
    db: Session,
    run_id: int,
) -> Optional[OptimizationRun]:

    return (
        db.query(OptimizationRun)
        .filter(
            OptimizationRun.run_id == run_id
        )
        .first()
    )


def get_recommendation(
    db: Session,
    recommendation_id: int,
) -> Optional[OptimizationRecommendation]:

    return (
        db.query(OptimizationRecommendation)
        .filter(
            OptimizationRecommendation.recommendation_id
            == recommendation_id
        )
        .first()
    )


def get_recommendations_for_run(
    db: Session,
    run_id: int,
) -> list[OptimizationRecommendation]:

    return (
        db.query(OptimizationRecommendation)
        .filter(
            OptimizationRecommendation.run_id
            == run_id
        )
        .order_by(
            OptimizationRecommendation.recommendation_id
        )
        .all()
    )

def get_decision_for_recommendation(
    db: Session,
    recommendation_id: int,
) -> Optional[RecommendationDecision]:

    return (
        db.query(RecommendationDecision)
        .filter(
            RecommendationDecision.recommendation_id
            == recommendation_id
        )
        .first()
    )


def get_decision(
    db: Session,
    decision_id: int,
) -> Optional[RecommendationDecision]:

    return (
        db.query(RecommendationDecision)
        .filter(
            RecommendationDecision.decision_id
            == decision_id
        )
        .first()
    )


def insert_recommendation_decision(
    db: Session,
    *,
    recommendation_id: int,
    decision_status: str,
    decided_by: Optional[str] = None,
    decision_note: Optional[str] = None,
) -> RecommendationDecision:

    # Accepted recommendations wait for execution.
    # Rejected recommendations will never be executed.
    execution_status = (
        "PENDING"
        if decision_status == "ACCEPTED"
        else "NOT_APPLICABLE"
    )

    decision = RecommendationDecision(
        recommendation_id=recommendation_id,
        decision_status=decision_status,
        execution_status=execution_status,
        decided_by=decided_by,
        decision_note=decision_note,
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision

def mark_decision_executed(
    db: Session,
    decision_id: int,
) -> Optional[RecommendationDecision]:

    decision = get_decision(
        db,
        decision_id,
    )

    if decision is None:
        return None

    decision.execution_status = "EXECUTED"
    decision.executed_at = func.now()

    db.commit()
    db.refresh(decision)

    return decision