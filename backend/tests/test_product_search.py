import asyncio
import pytest
from app.services.product_service import product_service
from app.schemas.product import ProductFilterRequest

def test_search_by_category():
    results = asyncio.run(product_service.search(ProductFilterRequest(category="Running Shoes")))
    assert len(results) > 0
    for p in results:
        assert p.category == "Running Shoes"

def test_search_with_max_price():
    # Running shoes under 3000
    results = asyncio.run(product_service.search(ProductFilterRequest(category="Running Shoes", max_price=3000)))
    assert len(results) > 0
    for p in results:
        assert p.price <= 3000
        assert p.category == "Running Shoes"

def test_search_by_color():
    results = asyncio.run(product_service.search(ProductFilterRequest(color="Black")))
    assert len(results) > 0
    for p in results:
        assert "black" in p.color.lower()

def test_search_by_shoe_size():
    results = asyncio.run(product_service.search(ProductFilterRequest(category="Running Shoes", size=9)))
    assert len(results) > 0
    for p in results:
        assert any(str(s) == "9" for s in p.sizes)

def test_get_by_id_found_and_not_found():
    product = asyncio.run(product_service.get_by_id("shoe_001"))
    assert product is not None
    assert product.id == "shoe_001"
    assert product.name == "Sprint X Running Shoes"

    missing = asyncio.run(product_service.get_by_id("non_existent_999"))
    assert missing is None
