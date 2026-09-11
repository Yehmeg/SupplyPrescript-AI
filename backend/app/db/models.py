from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    TIMESTAMP,
)

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func


Base = declarative_base()


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id = Column(Integer, primary_key=True)

    origin = Column(String(120), nullable=False)
    destination = Column(String(120), nullable=False)

    carrier = Column(String(120))
    product_type = Column(String(120))
    quantity = Column(Numeric)

    scheduled_ship_date = Column(TIMESTAMP)
    scheduled_delivery_date = Column(TIMESTAMP)

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    predictions = relationship(
        "Prediction",
        back_populates="shipment",
        cascade="all, delete",
    )

    decisions = relationship(
        "Decision",
        back_populates="shipment",
    )


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True)

    shipment_id = Column(
        Integer,
        ForeignKey(
            "shipments.shipment_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    risk_probability = Column(
        Numeric(5, 4),
        nullable=False,
    )

    predicted_class = Column(
        String(20),
        nullable=False,
    )

    model_version = Column(
        String(50),
        nullable=False,
    )

    eligibility_status = Column(
        String(30),
        nullable=False,
        default="eligible",
    )

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "risk_probability BETWEEN 0 AND 1",
            name="risk_probability_range",
        ),
    )

    shipment = relationship(
        "Shipment",
        back_populates="predictions",
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="prediction",
        cascade="all, delete",
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(
        Integer,
        primary_key=True,
    )

    prediction_id = Column(
        Integer,
        ForeignKey(
            "predictions.prediction_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    action_id = Column(
        String(50),
        nullable=False,
    )

    action_name = Column(
        String(120),
        nullable=False,
    )

    predicted_cost = Column(
        Numeric(12, 2),
        nullable=False,
    )

    predicted_time_days = Column(
        Numeric(6, 2),
        nullable=False,
    )

    risk_score = Column(
        Numeric(5, 4),
    )

    feasible = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    reason = Column(Text)

    rank = Column(SmallInteger)

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    prediction = relationship(
        "Prediction",
        back_populates="recommendations",
    )

    decisions = relationship(
        "Decision",
        back_populates="recommendation",
    )


class Decision(Base):
    __tablename__ = "decisions"

    decision_id = Column(
        Integer,
        primary_key=True,
    )

    recommendation_id = Column(
        Integer,
        ForeignKey(
            "recommendations.recommendation_id"
        ),
        nullable=False,
    )

    shipment_id = Column(
        Integer,
        ForeignKey("shipments.shipment_id"),
        nullable=False,
    )

    executed_by = Column(String(120))

    status = Column(
        String(30),
        nullable=False,
        default="executed",
    )

    predicted_cost_at_exec = Column(
        Numeric(12, 2),
        nullable=False,
    )

    predicted_time_at_exec = Column(
        Numeric(6, 2),
        nullable=False,
    )

    executed_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    recommendation = relationship(
        "Recommendation",
        back_populates="decisions",
    )

    shipment = relationship(
        "Shipment",
        back_populates="decisions",
    )

    outcome = relationship(
        "Outcome",
        back_populates="decision",
        uselist=False,
        cascade="all, delete",
    )


class Outcome(Base):
    __tablename__ = "outcomes"

    outcome_id = Column(
        Integer,
        primary_key=True,
    )

    decision_id = Column(
        Integer,
        ForeignKey(
            "decisions.decision_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    actual_cost = Column(Numeric(12, 2))
    actual_time_days = Column(Numeric(6, 2))
    actual_delayed = Column(Boolean)

    recorded_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    decision = relationship(
        "Decision",
        back_populates="outcome",
    )