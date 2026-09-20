import pytest
from app.utils.language import (
    detect_language,
    extract_price_from_text,
    extract_size_from_text,
    extract_color_from_text,
    match_category,
    detect_rule_based_intent
)

def test_hinglish_language_detection():
    assert detect_language("Running shoes dikhao under 3000") == "hinglish"
    assert detect_language("Mujhe black sneakers chahiye") == "hinglish"
    assert detect_language("Iska discount kitna hai?") == "hinglish"
    assert detect_language("Ye shoes size 9 mein available hai kya?") == "hinglish"
    assert detect_language("Show me running shoes under 3000") == "en"

def test_price_extraction():
    _, max_p = extract_price_from_text("running shoes under 3000")
    assert max_p == 3000

    _, max_p2 = extract_price_from_text("3000 ke andar")
    assert max_p2 == 3000

    _, max_p3 = extract_price_from_text("budget 2500 hai")
    assert max_p3 == 2500

    min_p, max_p4 = extract_price_from_text("between 2000 and 4000")
    assert min_p == 2000
    assert max_p4 == 4000

def test_size_extraction():
    assert extract_size_from_text("size 9 mein available hai") == 9
    assert extract_size_from_text("show me size 10 shoes") == 10

def test_color_extraction():
    assert extract_color_from_text("mujhe black sneakers chahiye") == "Black"
    assert extract_color_from_text("show white running shoes") == "White"

def test_category_matching():
    assert match_category("running shoes dikhao") == "Running Shoes"
    assert match_category("mujhe black sneakers chahiye") == "Sneakers"
    assert match_category("anc headphones") == "Headphones"
    assert match_category("best laptop for student") == "Laptops"

def test_intent_detection():
    assert detect_rule_based_intent("Iska discount kitna hai?") == "discount_query"
    assert detect_rule_based_intent("Compare Sprint X and Runner Pro") == "product_comparison"
    assert detect_rule_based_intent("ye size 9 mein available hai kya?") == "availability_query"
    assert detect_rule_based_intent("budget 2500 hai, kuch achha suggest karo") == "product_recommendation"
    assert detect_rule_based_intent("show me running shoes under 3000") == "product_search"
