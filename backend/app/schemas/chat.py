from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.product import Product

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    language_hint: Optional[str] = None
    voice_input: bool = True
    context_product_id: Optional[str] = None

class LatencyMetrics(BaseModel):
    intent_ms: float = 0.0
    retrieval_ms: float = 0.0
    pricing_ms: float = 0.0
    llm_ms: float = 0.0
    validation_ms: float = 0.0
    total_ms: float = 0.0

class DebugInfo(BaseModel):
    session_id: str
    detected_intent: str
    extracted_entities: Dict[str, Any]
    detected_language: str
    rag_used: bool
    rag_sources: List[str] = Field(default_factory=list)
    pricing_authoritative: Optional[Dict[str, Any]] = None
    prompt_version: str
    validation_passed: bool
    validation_notes: List[str] = Field(default_factory=list)
    latency: LatencyMetrics

class SpokenOutput(BaseModel):
    text: str
    ssml: Optional[str] = None
    language_code: str = "en-IN"  # "en-IN" or "hi-IN"
    speech_rate: float = 1.0

class ChatResponse(BaseModel):
    session_id: str
    display_response: str
    spoken_response: SpokenOutput
    products: List[Product] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    comparison: Optional[Dict[str, Any]] = None
    debug: Optional[DebugInfo] = None

class RagQueryRequest(BaseModel):
    query: str
    top_k: int = 4
    category: Optional[str] = None

class RagQueryResponse(BaseModel):
    query: str
    retrieved_chunks: List[Dict[str, Any]]
    answer: str
    source_products: List[str]
