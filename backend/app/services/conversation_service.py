import uuid
from typing import Dict, Optional, Any
from datetime import datetime
from app.models.conversation import ConversationState, Message, ConversationFilter

class ConversationService:
    """
    Session and multi-turn state management.
    Retains conversational memory across multiple voice interactions:
    User: "Mujhe running shoes chahiye." -> Assistant: "What is your budget?"
    User: "Around 3000." -> Assistant: "Got it. I found 5 running shoes under ₹3,000."
    """

    def __init__(self):
        self._sessions: Dict[str, ConversationState] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> ConversationState:
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())
            self._sessions[new_id] = ConversationState(session_id=new_id)
            return self._sessions[new_id]
        return self._sessions[session_id]

    def add_user_message(self, session_id: str, content: str, intent: Optional[str] = None) -> ConversationState:
        state = self.get_or_create_session(session_id)
        state.history.append(Message(role="user", content=content, intent=intent))
        state.last_updated = datetime.utcnow()
        return state

    def add_assistant_message(self, session_id: str, content: str) -> ConversationState:
        state = self.get_or_create_session(session_id)
        state.history.append(Message(role="assistant", content=content))
        state.last_updated = datetime.utcnow()
        return state

    def update_state(
        self,
        session_id: str,
        detected_intent: Optional[str] = None,
        extracted_entities: Optional[Dict[str, Any]] = None,
        last_retrieved_product_ids: Optional[list] = None,
        context_product_id: Optional[str] = None,
        language_preference: Optional[str] = None
    ) -> ConversationState:
        state = self.get_or_create_session(session_id)

        if detected_intent:
            state.detected_intent = detected_intent

        if extracted_entities:
            # Merge entities
            for k, v in extracted_entities.items():
                if v is not None:
                    state.extracted_entities[k] = v

            # Update accumulated filters
            if extracted_entities.get("category"):
                state.current_filters.category = extracted_entities["category"]
            if extracted_entities.get("color"):
                state.current_filters.color = extracted_entities["color"]
            if extracted_entities.get("size"):
                state.current_filters.size = str(extracted_entities["size"])
            if extracted_entities.get("min_price") is not None:
                state.current_filters.min_price = extracted_entities["min_price"]
            if extracted_entities.get("max_price") is not None:
                state.current_filters.max_price = extracted_entities["max_price"]

        if last_retrieved_product_ids:
            state.last_retrieved_product_ids = last_retrieved_product_ids
            if not context_product_id and len(last_retrieved_product_ids) > 0:
                # Set first retrieved as active candidate
                state.current_product_context = last_retrieved_product_ids[0]

        if context_product_id:
            state.current_product_context = context_product_id

        if language_preference:
            state.language_preference = language_preference

        state.last_updated = datetime.utcnow()
        return state

    def get_state(self, session_id: str) -> Optional[ConversationState]:
        return self._sessions.get(session_id)

    def reset_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

conversation_service = ConversationService()
