import asyncio
import pytest
from app.schemas.chat import ChatRequest
from app.api.routes.chat import chat_interaction
from app.services.product_service import product_service
from app.services.rag_service import rag_service
from app.services.voice_service import VoiceService

@pytest.fixture(autouse=True, scope="module")
def setup_catalog():
    products = asyncio.run(product_service.get_all())
    rag_service.build_index(products)

def test_voice_text_cleaning():
    text = "Sprint X is ₹2,499. It has ANC and 60-hour playtime."
    cleaned = VoiceService.clean_text_for_speech(text)
    assert "2,499 rupees" in cleaned
    assert "Active Noise Cancellation" in cleaned
    assert "₹" not in cleaned

def test_multi_turn_voice_flow():
    # Turn 1: Search in Hinglish
    req1 = ChatRequest(query="Mujhe running shoes chahiye under 3000", session_id="test_sess_001")
    res1 = asyncio.run(chat_interaction(req1))
    assert res1.session_id == "test_sess_001"
    assert len(res1.products) > 0
    assert res1.debug.detected_intent == "product_search"
    assert res1.spoken_response.text != ""

    # Turn 2: Ask discount on top result
    top_product_id = res1.products[0].id
    req2 = ChatRequest(query="Iska discount kitna hai?", session_id="test_sess_001", context_product_id=top_product_id)
    res2 = asyncio.run(chat_interaction(req2))
    assert res2.session_id == "test_sess_001"
    assert res2.debug.detected_intent == "discount_query"
    assert "discount" in res2.display_response.lower() or "%" in res2.display_response

    # Turn 3: Check size 9 availability
    req3 = ChatRequest(query="ye shoes size 9 mein available hai kya?", session_id="test_sess_001")
    res3 = asyncio.run(chat_interaction(req3))
    assert res3.debug.detected_intent == "availability_query"
    assert "available" in res3.display_response.lower()
