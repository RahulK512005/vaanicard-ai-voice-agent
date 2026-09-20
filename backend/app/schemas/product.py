from typing import List, Optional, Union
from pydantic import BaseModel, Field
from app.models.product import Product

class ProductFilterRequest(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    size: Optional[Union[int, str]] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_rating: Optional[float] = None
    tags: Optional[List[str]] = None
    in_stock_only: bool = True
    query: Optional[str] = None
    sort_by: Optional[str] = "relevance"  # "price_asc", "price_desc", "rating", "discount"
    limit: int = 10
    offset: int = 0

class ProductSearchResponse(BaseModel):
    total: int
    products: List[Product]
    categories: List[str]
    applied_filters: dict

class PriceCalculationRequest(BaseModel):
    product_id: str
    quantity: int = 1
    coupon_code: Optional[str] = None

class PriceCalculationResponse(BaseModel):
    product_id: str
    product_name: str
    original_mrp: int
    base_price: int
    unit_discount_amount: int
    unit_discount_percentage: int
    quantity: int
    subtotal: int
    coupon_code: Optional[str] = None
    coupon_discount: int = 0
    coupon_applied_success: bool = False
    coupon_message: Optional[str] = None
    gst_amount: int = 0  # 18% inclusive or breakdown
    final_payable: int
    currency: str = "INR"

class ComparisonRequest(BaseModel):
    product_ids: List[str]
    attributes_to_highlight: Optional[List[str]] = None

class ComparisonResponse(BaseModel):
    products: List[Product]
    comparison_matrix: dict
    winner_summary: dict
    spoken_summary: str
