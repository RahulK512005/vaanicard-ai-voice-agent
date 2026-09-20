from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None

class ConversationFilter(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_rating: Optional[float] = None
    query: Optional[str] = None

class ConversationState(BaseModel):
    session_id: str
    history: List[Message] = Field(default_factory=list)
    detected_intent: Optional[str] = None
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    current_product_context: Optional[str] = None  # e.g., product_id actively being discussed
    current_filters: ConversationFilter = Field(default_factory=ConversationFilter)
    language_preference: str = "hinglish"  # "en" | "hinglish" | "hi"
    last_retrieved_product_ids: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
