from fastapi import APIRouter, HTTPException
from app.schemas.product import PriceCalculationRequest, PriceCalculationResponse
from app.services.product_service import product_service
from app.services.pricing_service import PricingService

router = APIRouter(prefix="/api/calculate-price", tags=["Pricing"])

@router.post("", response_model=PriceCalculationResponse)
async def calculate_price(req: PriceCalculationRequest):
    """
    Authoritative pricing endpoint.
    Computes unit discount, quantity multiplier, coupon discount (e.g. VAANI100, FESTIVE20),
    GST breakdown, and final net payable price.
    """
    product = await product_service.get_by_id(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID '{req.product_id}' not found")

    return PricingService.calculate_product_price(
        product=product,
        quantity=req.quantity,
        coupon_code=req.coupon_code
    )
