import asyncio
import pytest
from app.services.product_service import product_service
from app.services.rag_service import rag_service
from app.services.validation_service import ValidationService

@pytest.fixture(autouse=True, scope="module")
def init_rag():
    products = asyncio.run(product_service.get_all())
    rag_service.build_index(products)

def test_rag_semantic_search_noise_cancellation():
    results = rag_service.search("Which headphones have noise cancellation?", top_k=2)
    assert len(results) > 0
    top_chunk = results[0]
    # AcousticPro or SonicAir have ANC
    assert "Noise Cancellation" in top_chunk["text"] or "ANC" in top_chunk["text"]

def test_rag_semantic_search_battery_life():
    results = rag_service.search("Which laptop has the best battery life?", top_k=2)
    assert len(results) > 0
    assert any("battery" in r["text"].lower() for r in results)

def test_response_validation_sentence_length_limit():
    long_text = "First sentence here. Second sentence here. Third sentence here. Fourth sentence here. Fifth sentence should be trimmed."
    is_valid, sanitized, notes = ValidationService.validate_and_sanitize(long_text, retrieved_products=[])
    assert is_valid is False
    assert "Fifth sentence" not in sanitized
    assert any("4 sentences" in n for n in notes)

def test_response_validation_markdown_cleaning():
    bullet_text = "Here are options:\n1. Sprint X\n2. Runner Pro"
    is_valid, sanitized, notes = ValidationService.validate_and_sanitize(bullet_text, retrieved_products=[])
    assert is_valid is False
    assert "1. " not in sanitized
    assert "2. " not in sanitized
