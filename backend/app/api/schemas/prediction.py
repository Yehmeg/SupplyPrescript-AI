from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class OrderInput(BaseModel):
    """Single order for risk scoring. All 32 features required (exact V2 schema)."""
    Type: str
    Days_for_shipment_scheduled: int = Field(alias="Days for shipment (scheduled)")
    Benefit_per_order: float = Field(alias="Benefit per order")
    Sales_per_customer: float = Field(alias="Sales per customer")
    Category_Name: str = Field(alias="Category Name")
    Customer_City: str = Field(alias="Customer City")
    Customer_Country: str = Field(alias="Customer Country")
    Customer_Segment: str = Field(alias="Customer Segment")
    Customer_State: str = Field(alias="Customer State")
    Department_Name: str = Field(alias="Department Name")
    Latitude: float
    Longitude: float
    Market: str
    Order_City: str = Field(alias="Order City")
    Order_Country: str = Field(alias="Order Country")
    Order_Item_Discount: float = Field(alias="Order Item Discount")
    Order_Item_Discount_Rate: float = Field(alias="Order Item Discount Rate")
    Order_Item_Product_Price: float = Field(alias="Order Item Product Price")
    Order_Item_Profit_Ratio: float = Field(alias="Order Item Profit Ratio")
    Order_Item_Quantity: int = Field(alias="Order Item Quantity")
    Sales: float
    Order_Item_Total: float = Field(alias="Order Item Total")
    Order_Profit_Per_Order: float = Field(alias="Order Profit Per Order")
    Order_Region: str = Field(alias="Order Region")
    Order_State: str = Field(alias="Order State")
    Product_Category_Id: int = Field(alias="Product Category Id")
    Product_Name: str = Field(alias="Product Name")
    Product_Price: float = Field(alias="Product Price")
    Order_Year: int = Field(alias="Order_Year")
    Order_Month: int = Field(alias="Order_Month")
    Order_DayOfWeek: int = Field(alias="Order_DayOfWeek")
    Order_Day: int = Field(alias="Order_Day")
    Order_Status: Optional[str] = Field(default=None, alias="Order Status")

    model_config = ConfigDict(populate_by_name=True)


class PredictRequest(BaseModel):
    orders: List[OrderInput]
    request_id: Optional[str] = None


class PredictionResponseItem(BaseModel):
    """Matches supplyprescript.inference.schema.PredictionOutput"""
    Late_Risk_Probability: Optional[float] = None
    Predicted_Late_Risk: Optional[int] = None
    Prediction_Eligible: bool
    Exclusion_Reason: Optional[str] = None


class PredictResponse(BaseModel):
    request_id: Optional[str] = None
    predictions: List[PredictionResponseItem]
    model_version: str = "SupplyPrescript ML V2"
    threshold_used: float = 0.18