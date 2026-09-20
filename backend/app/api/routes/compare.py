from fastapi import APIRouter, HTTPException
from app.schemas.product import ComparisonRequest, ComparisonResponse
from app.services.product_service import product_service
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/api/compare", tags=["Comparison"])

@router.post("", response_model=ComparisonResponse)
async def compare_products(req: ComparisonRequest):
    """
    Compares 2 or more products side-by-side on price, rating, key features, and specs.
    Generates structured comparison matrix and concise spoken audio summary.
    """
    if len(req.product_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 product IDs are required for comparison.")

    products = await product_service.get_by_ids(req.product_ids)
    if len(products) < 2:
        raise HTTPException(status_code=404, detail="One or more specified products could not be found.")

    p1, p2 = products[0], products[1]

    # Build side-by-side comparison matrix
    matrix = {
        "names": [p.name for p in products],
        "prices": [f"₹{p.price:,}" for p in products],
        "ratings": [f"{p.rating} / 5" for p in products],
        "discounts": [f"{p.discount_percentage}% OFF" for p in products],
        "colors": [p.color for p in products],
        "top_features": [p.features[0] if p.features else "Standard quality" for p in products]
    }

    cheaper = p1 if p1.price <= p2.price else p2
    higher_rated = p1 if p1.rating >= p2.rating else p2

    winner_summary = {
        "best_value": cheaper.name,
        "price_difference": abs(p1.price - p2.price),
        "highest_rated": higher_rated.name
    }

    spoken = (
        f"{p1.name} is priced at ₹{p1.price:,}, while {p2.name} is ₹{p2.price:,}. "
        f"{cheaper.name} is more affordable by ₹{abs(p1.price - p2.price):,}. "
        f"Which matters more to you, price or user rating?"
    )

    return ComparisonResponse(
        products=products,
        comparison_matrix=matrix,
        winner_summary=winner_summary,
        spoken_summary=VoiceService.clean_text_for_speech(spoken)
    )
