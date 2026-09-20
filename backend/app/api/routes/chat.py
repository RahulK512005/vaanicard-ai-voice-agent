import time
import logging
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse, DebugInfo, LatencyMetrics
from app.schemas.product import ProductFilterRequest
from app.services.conversation_service import conversation_service
from app.services.product_service import product_service
from app.services.pricing_service import PricingService
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.prompt_service import prompt_service
from app.services.validation_service import ValidationService
from app.services.voice_service import VoiceService
from app.utils.language import detect_language

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat & Voice"])

@router.post("", response_model=ChatResponse)
async def chat_interaction(req: ChatRequest):
    t_start = time.perf_counter()

    # 1. Conversation State initialization
    state = conversation_service.get_or_create_session(req.session_id)
    conversation_service.add_user_message(state.session_id, req.query)

    # Detect language (Hinglish or English)
    detected_lang = req.language_hint or detect_language(req.query)

    # 2. Intent Detection & Entity Extraction
    t_intent_start = time.perf_counter()
    extracted = await llm_service.extract_intent_and_entities(
        query=req.query,
        context_state={
            "current_product_context": req.context_product_id or state.current_product_context,
            "last_filters": state.current_filters.model_dump()
        }
    )
    t_intent_end = time.perf_counter()
    intent = extracted.get("intent", "product_search")

    # Merge entities into conversation state
    state = conversation_service.update_state(
        session_id=state.session_id,
        detected_intent=intent,
        extracted_entities=extracted,
        context_product_id=req.context_product_id,
        language_preference=detected_lang
    )

    # 3. Product Catalog Retrieval & Filtering
    t_retrieval_start = time.perf_counter()
    search_category = extracted.get("category") or state.current_filters.category
    search_max_price = extracted.get("max_price") or state.current_filters.max_price
    search_min_price = extracted.get("min_price") or state.current_filters.min_price
    search_color = extracted.get("color") or state.current_filters.color
    search_size = extracted.get("size") or state.current_filters.size

    filter_req = ProductFilterRequest(
        category=search_category,
        color=search_color,
        size=search_size,
        min_price=search_min_price,
        max_price=search_max_price,
        query=req.query if not search_category else None,
        sort_by=extracted.get("sort_by", "relevance"),
        limit=6
    )
    retrieved_products = await product_service.search(filter_req)

    # Fallback to general search if strict filters yield zero
    if not retrieved_products and search_category:
        filter_req_relaxed = ProductFilterRequest(category=search_category, limit=6)
        retrieved_products = await product_service.search(filter_req_relaxed)

    # If context product specified or follow-up discount query, make sure context product is first
    if state.current_product_context and (intent in ["discount_query", "price_query", "availability_query"]):
        ctx_p = await product_service.get_by_id(state.current_product_context)
        if ctx_p and ctx_p.id not in [p.id for p in retrieved_products]:
            retrieved_products.insert(0, ctx_p)
        elif ctx_p:
            # Move to front
            retrieved_products = [p for p in retrieved_products if p.id != ctx_p.id]
            retrieved_products.insert(0, ctx_p)

    retrieved_ids = [p.id for p in retrieved_products]
    conversation_service.update_state(
        session_id=state.session_id,
        last_retrieved_product_ids=retrieved_ids
    )
    t_retrieval_end = time.perf_counter()

    # 4. Authoritative Pricing Computation
    t_pricing_start = time.perf_counter()
    pricing_context = ""
    authoritative_pricing_dict = None
    if retrieved_products and (intent in ["discount_query", "price_query"] or extracted.get("coupon_code")):
        top_product = retrieved_products[0]
        calc = PricingService.calculate_product_price(
            product=top_product,
            coupon_code=extracted.get("coupon_code")
        )
        pricing_context = PricingService.get_summary_for_llm(calc)
        authoritative_pricing_dict = calc.model_dump()
    t_pricing_end = time.perf_counter()

    # 5. RAG Retrieval if specs/comparison/knowledge question
    rag_used = False
    rag_context = ""
    rag_sources = []
    if intent in ["product_details", "product_comparison"] or any(k in req.query.lower() for k in ["running", "anc", "battery", "cushion", "lightweight", "noise"]):
        rag_used = True
        rag_results = rag_service.search(req.query, top_k=3, category_filter=search_category)
        if rag_results:
            rag_context = rag_service.get_grounded_context_string(req.query, top_k=3)
            rag_sources = [r["product_name"] for r in rag_results]

    # 6. Comparison Generation if Comparison intent
    comparison_data = None
    if intent == "product_comparison" and len(retrieved_products) >= 2:
        p1, p2 = retrieved_products[0], retrieved_products[1]
        comparison_data = {
            "products": [p1.model_dump(), p2.model_dump()],
            "price_diff": abs(p1.price - p2.price),
            "cheaper": p1.name if p1.price < p2.price else p2.name,
            "higher_rated": p1.name if p1.rating >= p2.rating else p2.name
        }

    # 7. LLM Spoken Response Generation
    t_llm_start = time.perf_counter()
    system_prompt = prompt_service.get_voice_prompt()
    raw_response = await llm_service.generate_voice_response(
        query=req.query,
        intent=intent,
        retrieved_products=retrieved_products,
        rag_context=rag_context,
        pricing_context=pricing_context,
        language=detected_lang,
        system_prompt=system_prompt
    )
    t_llm_end = time.perf_counter()

    # 8. Guardrail Validation
    t_val_start = time.perf_counter()
    is_valid, validated_text, val_notes = ValidationService.validate_and_sanitize(
        response_text=raw_response,
        retrieved_products=retrieved_products,
        pricing_data=authoritative_pricing_dict
    )
    t_val_end = time.perf_counter()

    # Record assistant message in conversation
    conversation_service.add_assistant_message(state.session_id, validated_text)

    # 9. Voice Audio Formatting
    spoken_output = VoiceService.prepare_spoken_output(validated_text, language_preference=detected_lang)

    # Suggested actions chips
    suggested_actions = []
    if retrieved_products:
        if len(retrieved_products) >= 2:
            suggested_actions.append(f"Compare {retrieved_products[0].name} & {retrieved_products[1].name}")
        suggested_actions.append("Iska discount kitna hai?")
        suggested_actions.append("Check size 9 availability")
        suggested_actions.append("Show something cheaper")

    t_total = time.perf_counter() - t_start

    # Latency Metrics
    latency = LatencyMetrics(
        intent_ms=round((t_intent_end - t_intent_start) * 1000, 2),
        retrieval_ms=round((t_retrieval_end - t_retrieval_start) * 1000, 2),
        pricing_ms=round((t_pricing_end - t_pricing_start) * 1000, 2),
        llm_ms=round((t_llm_end - t_llm_start) * 1000, 2),
        validation_ms=round((t_val_end - t_val_start) * 1000, 2),
        total_ms=round(t_total * 1000, 2)
    )

    debug_info = DebugInfo(
        session_id=state.session_id,
        detected_intent=intent,
        extracted_entities=extracted,
        detected_language=detected_lang,
        rag_used=rag_used,
        rag_sources=rag_sources,
        pricing_authoritative=authoritative_pricing_dict,
        prompt_version=prompt_service.get_voice_prompt()[:30] + "...",
        validation_passed=is_valid,
        validation_notes=val_notes,
        latency=latency
    )

    return ChatResponse(
        session_id=state.session_id,
        display_response=validated_text,
        spoken_response=spoken_output,
        products=retrieved_products,
        suggested_actions=suggested_actions,
        comparison=comparison_data,
        debug=debug_info
    )
