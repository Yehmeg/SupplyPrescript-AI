import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture
async def async_client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


# Sample valid order data matching V2 32-feature schema
SAMPLE_ORDER = {
    "Type": "DEBIT",
    "Days for shipment (scheduled)": 4,
    "Benefit per order": 91.25,
    "Sales per customer": 314.64,
    "Category Name": "Sporting Goods",
    "Customer City": "Caguas",
    "Customer Country": "Puerto Rico",
    "Customer Segment": "Consumer",
    "Customer State": "PR",
    "Department Name": "Fitness",
    "Latitude": 18.2514534,
    "Longitude": -66.03705597,
    "Market": "Pacific Asia",
    "Order City": "Bekasi",
    "Order Country": "Indonesia",
    "Order Item Discount": 13.11,
    "Order Item Discount Rate": 0.04,
    "Order Item Product Price": 327.75,
    "Order Item Profit Ratio": 0.29,
    "Order Item Quantity": 1,
    "Sales": 327.75,
    "Order Item Total": 314.64,
    "Order Profit Per Order": 91.25,
    "Order Region": "Southeast Asia",
    "Order State": "Java Occidental",
    "Product Category Id": 73,
    "Product Name": "Smart watch",
    "Product Price": 327.75,
    "Order_Year": 2018,
    "Order_Month": 1,
    "Order_DayOfWeek": 2,
    "Order_Day": 31,
}


@pytest.fixture
def sample_order():
    return SAMPLE_ORDER.copy()