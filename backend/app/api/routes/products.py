from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.product import Product
from app.schemas.product import ProductFilterRequest, ProductSearchResponse
from app.services.product_service import product_service

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=List[Product])
async def list_products(
    category: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """List products with optional category filter and pagination."""
    filters = ProductFilterRequest(category=category, limit=limit, offset=offset)
    return await product_service.search(filters)

@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get all unique product categories."""
    return await product_service.get_categories()

@router.get("/{product_id}", response_model=Product)
async def get_product_by_id(product_id: str):
    """Retrieve details of a single product."""
    product = await product_service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")
    return product

@router.post("/search", response_model=ProductSearchResponse)
async def search_products(filters: ProductFilterRequest):
    """Multi-facet product search supporting category, price range, color, size, rating, and keyword."""
    products = await product_service.search(filters)
    categories = await product_service.get_categories()
    return ProductSearchResponse(
        total=len(products),
        products=products,
        categories=categories,
        applied_filters=filters.model_dump()
    )
