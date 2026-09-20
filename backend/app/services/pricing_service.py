from typing import Optional, Dict
from app.models.product import Product
from app.schemas.product import PriceCalculationResponse

class PricingService:
    """
    Authoritative, deterministic price calculation engine.
    LLMs are explicitly prohibited from performing authoritative math.
    All coupons, discounts, taxes, and totals are computed strictly here.
    """

    AVAILABLE_COUPONS = {
        "VAANI100": {
            "type": "flat",
            "amount": 100,
            "min_order": 999,
            "description": "Flat ₹100 off on orders above ₹999"
        },
        "FESTIVE20": {
            "type": "percentage",
            "percentage": 20,
            "max_discount": 500,
            "min_order": 1499,
            "description": "20% off up to ₹500 on orders above ₹1499"
        },
        "WELCOME50": {
            "type": "flat",
            "amount": 50,
            "min_order": 499,
            "description": "Flat ₹50 off for new voice shoppers"
        }
    }

    @classmethod
    def calculate_product_price(
        cls,
        product: Product,
        quantity: int = 1,
        coupon_code: Optional[str] = None
    ) -> PriceCalculationResponse:
        if quantity <= 0:
            quantity = 1

        original_mrp = product.original_price
        base_price = product.price
        unit_discount_amount = max(0, original_mrp - base_price)
        unit_discount_percentage = int(round((unit_discount_amount / original_mrp) * 100)) if original_mrp > 0 else 0

        subtotal = base_price * quantity
        coupon_discount = 0
        coupon_applied_success = False
        coupon_message = None

        if coupon_code:
            code_upper = coupon_code.strip().upper()
            if code_upper in cls.AVAILABLE_COUPONS:
                rule = cls.AVAILABLE_COUPONS[code_upper]
                if subtotal >= rule["min_order"]:
                    if rule["type"] == "flat":
                        coupon_discount = rule["amount"]
                    elif rule["type"] == "percentage":
                        raw_discount = int(round(subtotal * (rule["percentage"] / 100)))
                        coupon_discount = min(raw_discount, rule["max_discount"])
                    
                    coupon_applied_success = True
                    coupon_message = f"Coupon '{code_upper}' applied: {rule['description']}"
                else:
                    coupon_message = f"Coupon '{code_upper}' requires a minimum order of ₹{rule['min_order']}."
            else:
                coupon_message = f"Coupon code '{coupon_code}' is invalid or expired."

        # Compute final payable
        final_payable = max(0, subtotal - coupon_discount)

        # 18% GST estimate component (for display context, prices are GST-inclusive in India)
        gst_amount = int(round(final_payable * 18 / 118))

        return PriceCalculationResponse(
            product_id=product.id,
            product_name=product.name,
            original_mrp=original_mrp,
            base_price=base_price,
            unit_discount_amount=unit_discount_amount,
            unit_discount_percentage=unit_discount_percentage,
            quantity=quantity,
            subtotal=subtotal,
            coupon_code=coupon_code.upper() if coupon_code else None,
            coupon_discount=coupon_discount,
            coupon_applied_success=coupon_applied_success,
            coupon_message=coupon_message,
            gst_amount=gst_amount,
            final_payable=final_payable,
            currency="INR"
        )

    @classmethod
    def get_summary_for_llm(cls, calc: PriceCalculationResponse) -> str:
        """Generates an unambiguous, verified summary string for LLM context injection."""
        summary = (
            f"VERIFIED AUTHORITATIVE PRICING for {calc.product_name}:\n"
            f"- MRP: ₹{calc.original_mrp:,}\n"
            f"- Current Price: ₹{calc.base_price:,} (Save ₹{calc.unit_discount_amount:,}, {calc.unit_discount_percentage}% OFF)\n"
        )
        if calc.coupon_applied_success:
            summary += (
                f"- Coupon '{calc.coupon_code}' Applied: -₹{calc.coupon_discount:,}\n"
                f"- Final Payable Price: ₹{calc.final_payable:,}\n"
            )
        else:
            summary += f"- Final Payable Price: ₹{calc.final_payable:,}\n"
        return summary
