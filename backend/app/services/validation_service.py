import re
from typing import List, Dict, Any, Tuple
from app.models.product import Product

class ValidationService:
    """
    Guardrails service.
    Validates LLM-generated responses against authoritative backend data before sending to user.
    """

    @classmethod
    def validate_and_sanitize(
        cls,
        response_text: str,
        retrieved_products: List[Product],
        pricing_data: Dict[str, Any] = None
    ) -> Tuple[bool, str, List[str]]:
        notes = []
        is_valid = True
        sanitized = response_text

        # 1. Check Voice Length: Count sentences
        sentences = [s.strip() for s in re.split(r"[.!?]+", sanitized) if len(s.strip()) > 3]
        if len(sentences) > 4:
            notes.append("Response exceeded 4 sentences; truncated to keep voice-friendly.")
            sanitized = ". ".join(sentences[:3]) + "."
            is_valid = False

        # 2. Check for disallowed markdown lists (e.g. '1. ', '- ', '* ')
        if re.search(r"^\s*(?:[\-\*]|\d+\.)\s+", response_text, flags=re.MULTILINE):
            notes.append("Response contained markdown list markers; cleaned for voice output.")
            # Remove bullet and numbered markers at line start
            sanitized = re.sub(r"^\s*(?:[\-\*]|\d+\.)\s*", "", sanitized, flags=re.MULTILINE)
            is_valid = False

        # 3. Check for raw URLs
        if re.search(r"https?://\S+", response_text):
            notes.append("Disallowed URL detected in voice response; stripped.")
            sanitized = re.sub(r"https?://\S+", "", sanitized)
            is_valid = False

        # 4. Verify any mentioned product prices match authoritative prices
        mentioned_prices = re.findall(r"(?:₹|Rs\.?\s*)(\d+[\d,]*)", response_text)
        valid_prices = set()
        for p in retrieved_products:
            valid_prices.add(p.price)
            valid_prices.add(p.original_price)
            if p.discount_amount:
                valid_prices.add(p.discount_amount)
        if pricing_data and "final_payable" in pricing_data:
            valid_prices.add(pricing_data["final_payable"])
            valid_prices.add(pricing_data["base_price"])

        for price_str in mentioned_prices:
            num = int(price_str.replace(",", ""))
            if valid_prices and num not in valid_prices and num > 50:
                notes.append(f"Price ₹{num} not verified in retrieved catalog items.")
                is_valid = False

        # 5. Fallback check: If empty or corrupt
        if not sanitized.strip():
            sanitized = "I found these options in the catalog for you. Would you like to hear more details?"
            notes.append("Response was empty; applied safe default.")
            is_valid = False

        return is_valid, sanitized, notes
