from fastapi import APIRouter
from typing import List, Optional
from app.models.product import Product
from app.schemas.product import ProductFilterRequest
from app.services.product_service import product_service

router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])

@router.post("", response_model=List[Product])
async def get_recommendations(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    sort_by: str = "rating"
):
    """Returns curated product recommendations based on top ratings and value."""
    filters = ProductFilterRequest(
        category=category,
        max_price=max_price,
        min_rating=4.2,
        sort_by=sort_by,
        limit=6
    )
    return await product_service.search(filters)
