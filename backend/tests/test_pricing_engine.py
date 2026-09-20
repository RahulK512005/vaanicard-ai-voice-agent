import pytest
from app.models.product import Product
from app.services.pricing_service import PricingService

@pytest.fixture
def sample_shoe():
    return Product(
        id="shoe_001",
        name="Sprint X Running Shoes",
        category="Running Shoes",
        brand="Velocity",
        description="Lightweight road running shoes",
        price=2499,
        original_price=3999,
        discount_percentage=37,
        color="Black",
        sizes=[7, 8, 9, 10],
        rating=4.4,
        stock=24,
        features=["Lightweight ZoomFoam midsole"],
        tags=["running", "lightweight"]
    )

def test_basic_price_and_discount_calculation(sample_shoe):
    calc = PricingService.calculate_product_price(sample_shoe, quantity=1)
    assert calc.product_id == "shoe_001"
    assert calc.original_mrp == 3999
    assert calc.base_price == 2499
    assert calc.unit_discount_amount == 1500
    assert calc.unit_discount_percentage == 38 or calc.unit_discount_percentage == 37  # rounded
    assert calc.subtotal == 2499
    assert calc.final_payable == 2499

def test_quantity_multiplier(sample_shoe):
    calc = PricingService.calculate_product_price(sample_shoe, quantity=2)
    assert calc.quantity == 2
    assert calc.subtotal == 4998
    assert calc.final_payable == 4998

def test_flat_coupon_application(sample_shoe):
    # VAANI100 gives flat 100 off on order >= 999
    calc = PricingService.calculate_product_price(sample_shoe, quantity=1, coupon_code="VAANI100")
    assert calc.coupon_applied_success is True
    assert calc.coupon_discount == 100
    assert calc.final_payable == 2399

def test_percentage_coupon_application(sample_shoe):
    # FESTIVE20 gives 20% off up to 500 on order >= 1499
    calc = PricingService.calculate_product_price(sample_shoe, quantity=1, coupon_code="FESTIVE20")
    assert calc.coupon_applied_success is True
    # 20% of 2499 is 499.8 -> 500 max capped
    assert calc.coupon_discount == 500
    assert calc.final_payable == 1999

def test_invalid_coupon(sample_shoe):
    calc = PricingService.calculate_product_price(sample_shoe, quantity=1, coupon_code="INVALID999")
    assert calc.coupon_applied_success is False
    assert calc.coupon_discount == 0
    assert calc.final_payable == 2499

def test_minimum_order_restriction():
    cheap_item = Product(
        id="cab_001",
        name="Cable",
        category="Mobile Accessories",
        brand="Volt",
        description="USB Cable",
        price=300,
        original_price=500,
        discount_percentage=40,
        color="Black",
        sizes=["1m"],
        rating=4.0,
        stock=10
    )
    # VAANI100 requires >= 999
    calc = PricingService.calculate_product_price(cheap_item, quantity=1, coupon_code="VAANI100")
    assert calc.coupon_applied_success is False
    assert calc.coupon_discount == 0
    assert calc.final_payable == 300
