from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(BigInteger, primary_key=True, autoincrement=True)

    order_type = Column("Type", String(50))
    days_for_shipment_scheduled = Column(
        "Days for shipment (scheduled)",
        Integer,
    )

    benefit_per_order = Column(
        "Benefit per order",
        Numeric(12, 2),
    )

    sales_per_customer = Column(
        "Sales per customer",
        Numeric(12, 2),
    )

    category_name = Column(
        "Category Name",
        String(150),
    )

    customer_city = Column(
        "Customer City",
        String(150),
    )

    customer_country = Column(
        "Customer Country",
        String(100),
    )

    customer_segment = Column(
        "Customer Segment",
        String(100),
    )

    customer_state = Column(
        "Customer State",
        String(100),
    )

    department_name = Column(
        "Department Name",
        String(100),
    )

    latitude = Column(
        "Latitude",
        Numeric(10, 7),
    )

    longitude = Column(
        "Longitude",
        Numeric(10, 7),
    )

    market = Column(
        "Market",
        String(100),
    )

    order_city = Column(
        "Order City",
        String(150),
    )

    order_country = Column(
        "Order Country",
        String(100),
    )

    order_item_discount = Column(
        "Order Item Discount",
        Numeric(12, 2),
    )

    order_item_discount_rate = Column(
        "Order Item Discount Rate",
        Numeric(8, 4),
    )

    order_item_product_price = Column(
        "Order Item Product Price",
        Numeric(12, 2),
    )

    order_item_profit_ratio = Column(
        "Order Item Profit Ratio",
        Numeric(8, 4),
    )

    order_item_quantity = Column(
        "Order Item Quantity",
        Integer,
    )

    sales = Column(
        "Sales",
        Numeric(12, 2),
    )

    order_item_total = Column(
        "Order Item Total",
        Numeric(12, 2),
    )

    order_profit_per_order = Column(
        "Order Profit Per Order",
        Numeric(12, 2),
    )

    order_region = Column(
        "Order Region",
        String(150),
    )

    order_state = Column(
        "Order State",
        String(150),
    )

    product_category_id = Column(
        "Product Category Id",
        Integer,
    )

    product_name = Column(
        "Product Name",
        String(255),
    )

    product_price = Column(
        "Product Price",
        Numeric(12, 2),
    )

    order_year = Column(
        "Order_Year",
        SmallInteger,
    )

    order_month = Column(
        "Order_Month",
        SmallInteger,
    )

    order_day_of_week = Column(
        "Order_DayOfWeek",
        SmallInteger,
    )

    order_day = Column(
        "Order_Day",
        SmallInteger,
    )

    order_status = Column(
        String(50),
    )

    received_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    source_system = Column(
        String(100),
    )

    raw_payload = Column(
        JSONB,
    )

    predictions = relationship(
        "MLPrediction",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    
    __table_args__ = (
    CheckConstraint(
        "late_risk_probability BETWEEN 0 AND 1",
        name="ck_ml_predictions_probability",
        ),
    )


    prediction_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    order_id = Column(
        BigInteger,
        ForeignKey(
            "orders.order_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    model_version = Column(
        String(100),
        nullable=False,
    )

    late_risk_probability = Column(
        Numeric(8, 6),
        nullable=False,
    )

    predicted_late_risk = Column(
        Boolean,
        nullable=False,
    )

    prediction_eligible = Column(
        Boolean,
        nullable=False,
    )

    exclusion_reason = Column(
        Text,
    )

    threshold_used = Column(
    Numeric(8, 6),
    nullable=False,
    server_default=text("0.18"),
    )

    ensemble_models_used = Column(
        ARRAY(Text),
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    request_id = Column(
        String(100),
    )

    order = relationship(
        "Order",
        back_populates="predictions",
    )

Index(
    "idx_ml_predictions_order",
    MLPrediction.order_id,
)

Index(
    "idx_ml_predictions_created_at",
    MLPrediction.created_at,
)