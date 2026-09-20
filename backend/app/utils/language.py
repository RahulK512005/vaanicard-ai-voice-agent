import re
from typing import Dict, Any, Optional, Tuple, List

# Indian English / Hinglish keyword patterns
HINGLISH_INDICATORS = [
    r"\bchahiye\b", r"\bdikhao\b", r"\bkitna\b", r"\bhai\b", r"\bka\b", r"\bki\b",
    r"\bmein\b", r"\bkya\b", r"\bkuch\b", r"\bachha\b", r"\baccha\b", r"\bsasta\b",
    r"\bmehenga\b", r"\bkam\b", r"\bdaam\b", r"\byeh\b", r"\bya\b", r"\bmujhe\b",
    r"\bhume\b", r"\bbolo\b", r"\bbatao\b", r"\bdena\b", r"\bkaro\b", r"\bke\s+andar\b"
]

CATEGORY_ALIASES = {
    "running shoes": ["running shoe", "running shoes", "runner", "runners", "running", "jogging shoe", "jogging shoes", "sports shoes"],
    "sneakers": ["sneaker", "sneakers", "casual shoes", "kicks", "canvas shoes"],
    "headphones": ["headphone", "headphones", "earbuds", "earbud", "earphone", "earphones", "tws", "airpods", "headset"],
    "smart watches": ["smart watch", "smartwatch", "smart watches", "smartwatches", "fitness band", "watch", "watches", "band"],
    "backpacks": ["backpack", "backpacks", "bag", "bags", "rucksack", "laptop bag", "school bag", "travel bag"],
    "t-shirts": ["t-shirt", "tshirt", "t-shirts", "tshirts", "tee", "tees", "shirt", "shirts", "polo"],
    "laptops": ["laptop", "laptops", "notebook", "computer", "macbook", "ultrabook", "pc"],
    "mobile accessories": ["mobile accessories", "power bank", "charger", "cable", "phone case", "car mount", "usb hub", "accessories"]
}

COLOR_PATTERNS = [
    "black", "white", "blue", "navy blue", "navy", "green", "olive green", "neon green",
    "grey", "gray", "red", "rose gold", "space grey", "silver", "teal", "khaki", "brown"
]

def detect_language(query: str) -> str:
    """Detect if the query has Hinglish elements or is English."""
    query_lower = query.lower()
    for pattern in HINGLISH_INDICATORS:
        if re.search(pattern, query_lower):
            return "hinglish"
    return "en"

def extract_price_from_text(query: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extracts min_price and max_price from patterns like:
    - 'under 3000', 'under ₹3,000', '3000 ke andar', 'below 2500'
    - 'budget 2500', 'budget 2000'
    - 'between 2000 and 4000', '2000 se 4000'
    """
    text = query.lower().replace(",", "").replace("₹", "").replace("rs.", "").replace("rs ", "").replace("inr", "")
    
    # Range: between X and Y or X se Y
    range_match = re.search(r"(?:between|from)?\s*(\d{2,6})\s*(?:and|to|se|-)\s*(\d{2,6})", text)
    if range_match:
        return int(range_match.group(1)), int(range_match.group(2))

    # Upper bound: under X, below X, X ke andar, budget X, less than X
    under_match = re.search(r"(?:under|below|less\s+than|budget(?:\s+is|\s+hai)?|max(?:imum)?)\s*(\d{2,6})", text)
    if under_match:
        return None, int(under_match.group(1))

    # Hindi 'X ke andar' or 'X tak'
    hindi_under = re.search(r"(\d{2,6})\s*(?:ke\s+andar|tak|mein)", text)
    if hindi_under:
        return None, int(hindi_under.group(1))

    # Lower bound: above X, more than X, min X
    above_match = re.search(r"(?:above|more\s+than|min(?:imum)?|over)\s*(\d{2,6})", text)
    if above_match:
        return int(above_match.group(1)), None

    return None, None

def extract_size_from_text(query: str) -> Optional[int]:
    """Extract shoe/apparel size like 'size 9', 'size 10', '9 number'."""
    text = query.lower()
    size_match = re.search(r"(?:size|number|no\.?)\s*(\d{1,2})", text)
    if size_match:
        return int(size_match.group(1))
    return None

def extract_color_from_text(query: str) -> Optional[str]:
    """Extract color from query string."""
    text = query.lower()
    for color in COLOR_PATTERNS:
        # Match word boundaries
        if re.search(rf"\b{re.escape(color)}\b", text):
            return color.capitalize()
    return None

def match_category(query: str) -> Optional[str]:
    """Match category based on query keywords."""
    text = query.lower()
    for cat_name, aliases in CATEGORY_ALIASES.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", text):
                # Standardize category title
                title_map = {
                    "running shoes": "Running Shoes",
                    "sneakers": "Sneakers",
                    "headphones": "Headphones",
                    "smart watches": "Smart Watches",
                    "backpacks": "Backpacks",
                    "t-shirts": "T-Shirts",
                    "laptops": "Laptops",
                    "mobile accessories": "Mobile Accessories"
                }
                return title_map.get(cat_name, cat_name.title())
    return None

def detect_rule_based_intent(query: str) -> str:
    """
    Classifies intent accurately from English and Hinglish expressions.
    Intents:
    - product_search
    - product_recommendation
    - product_comparison
    - price_query
    - discount_query
    - availability_query
    - product_details
    - general_shopping_question
    """
    text = query.lower()

    # Comparison
    if any(k in text for k in ["compare", "comparison", "dono mein se", "difference between", "better between", "versus", "vs"]):
        return "product_comparison"

    # Discount query
    if any(k in text for k in ["discount kitna", "kitna discount", "discount hai kya", "how much discount", "any discount", "coupon", "offer"]):
        return "discount_query"

    # Price query
    if any(k in text for k in ["kitne ka hai", "price kitna", "daam kitna", "what is the price", "how much does it cost", "cost kitna", "price kya hai"]):
        return "price_query"

    # Availability / size / stock query
    if any(k in text for k in ["available hai", "stock mein", "size 9 mein", "in stock", "is it available", "kya ye available"]):
        return "availability_query"

    # Recommendation
    if any(k in text for k in ["suggest karo", "recommend", "best", "achha", "accha", "top option", "something cheaper", "sasta", "which one should i buy"]):
        return "product_recommendation"

    # Product details / specs / features
    if any(k in text for k in ["specification", "specs", "features", "battery life", "noise cancellation", "anc", "material", "weight", "features kya"]):
        return "product_details"

    # Search
    if any(k in text for k in ["dikhao", "chahiye", "show me", "search", "find", "looking for", "under", "below"]):
        return "product_search"

    return "product_search"
