import json
import logging
import os
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.models.product import Product
from app.utils.language import (
    detect_language,
    detect_rule_based_intent,
    extract_price_from_text,
    extract_size_from_text,
    extract_color_from_text,
    match_category
)

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        self._init_providers()

    def _init_providers(self):
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_client = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini LLM configured with model: %s", settings.GEMINI_MODEL)
            except Exception as e:
                logger.warning("Failed to initialize Gemini: %s", e)

        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI LLM configured with model: %s", settings.OPENAI_MODEL)
            except Exception as e:
                logger.warning("Failed to initialize OpenAI: %s", e)

    async def extract_intent_and_entities(self, query: str, context_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extracts structured intent and shopping entities.
        Uses LLM if available; otherwise uses rule-based NLP extraction.
        """
        # If Gemini is configured, attempt prompt extraction
        if self.gemini_client:
            try:
                from app.services.prompt_service import prompt_service
                system_prompt = prompt_service.get_intent_prompt()
                prompt = f"{system_prompt}\n\nUser Query: \"{query}\"\nContext: {json.dumps(context_state or {})}\nJSON:"
                res = self.gemini_client.generate_content(prompt)
                raw_text = res.text.strip()
                # Clean code block backticks if present
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                parsed = json.loads(raw_text.strip())
                return parsed
            except Exception as e:
                logger.warning("Gemini intent extraction failed, falling back to rule parser: %s", e)

        # High-accuracy NLP Rule Extractor
        intent = detect_rule_based_intent(query)
        cat = match_category(query)
        color = extract_color_from_text(query)
        size = extract_size_from_text(query)
        min_p, max_p = extract_price_from_text(query)

        # Coupon detection
        coupon = None
        for code in ["VAANI100", "FESTIVE20", "WELCOME50"]:
            if code.lower() in query.lower():
                coupon = code

        # Product name target
        product_target = None
        if context_state and context_state.get("current_product_context"):
            product_target = context_state["current_product_context"]

        return {
            "intent": intent,
            "category": cat,
            "brand": None,
            "color": color,
            "size": size,
            "min_price": min_p,
            "max_price": max_p,
            "coupon_code": coupon,
            "product_target": product_target,
            "compare_targets": None,
            "sort_by": "price_asc" if "cheaper" in query.lower() or "sasta" in query.lower() else "relevance"
        }

    async def generate_voice_response(
        self,
        query: str,
        intent: str,
        retrieved_products: List[Product],
        rag_context: str = "",
        pricing_context: str = "",
        language: str = "hinglish",
        system_prompt: str = ""
    ) -> str:
        """
        Generates a 2-4 sentence voice-optimized shopping assistant response.
        Uses Gemini if available, else sophisticated rule-based generator.
        """
        if self.gemini_client:
            try:
                prompt = (
                    f"{system_prompt}\n\n"
                    f"User Query: \"{query}\"\n"
                    f"Detected Intent: {intent}\n"
                    f"Language Preference: {language}\n"
                    f"Authoritative Product Context:\n"
                )
                for p in retrieved_products[:3]:
                    prompt += f"- {p.name}: ₹{p.price:,} (MRP ₹{p.original_price:,}, {p.discount_percentage}% off), Rating {p.rating}/5, Stock {p.stock}\n"
                if pricing_context:
                    prompt += f"\n{pricing_context}\n"
                if rag_context:
                    prompt += f"\n{rag_context}\n"

                prompt += "\nRespond in 2-3 concise spoken sentences:"
                res = self.gemini_client.generate_content(prompt)
                return res.text.strip()
            except Exception as e:
                logger.warning("Gemini voice response generation failed, falling back: %s", e)

        # Heuristic Generator adhering to all Voice Rules
        return self._generate_heuristic_response(query, intent, retrieved_products, rag_context, pricing_context, language)

    def _generate_heuristic_response(
        self,
        query: str,
        intent: str,
        products: List[Product],
        rag_context: str,
        pricing_context: str,
        language: str
    ) -> str:
        is_hinglish = language == "hinglish" or detect_language(query) == "hinglish"
        count = len(products)

        if not products and not rag_context:
            if is_hinglish:
                return "Maaf kijiye, mujhe is request ke matching koi product nahi mila. Kya aap kisi aur category ya price range mein dekhna chahenge?"
            return "I couldn't find any products matching that specific criteria. Would you like to check a different category or price range?"

        # 1. Discount Query
        if intent == "discount_query" and products:
            p = products[0]
            if is_hinglish:
                return f"{p.name} par currently {p.discount_percentage}% discount mil raha hai. Iska original price ₹{p.original_price:,} tha aur current price ₹{p.price:,} hai."
            return f"{p.name} is currently {p.discount_percentage} percent off. The original price was ₹{p.original_price:,} and the current price is ₹{p.price:,}."

        # 2. Price Query
        if intent == "price_query" and products:
            p = products[0]
            if is_hinglish:
                return f"{p.name} ka price ₹{p.price:,} hai. Is par {p.discount_percentage}% ki bachat hai."
            return f"The current price of {p.name} is ₹{p.price:,}, which includes a {p.discount_percentage} percent discount."

        # 3. Availability / Size query
        if intent == "availability_query" and products:
            p = products[0]
            size = extract_size_from_text(query)
            if size:
                has_size = any(str(size) == str(s) for s in p.sizes)
                if has_size:
                    if is_hinglish:
                        return f"Haan! {p.name} size {size} mein available hai, aur currently {p.stock} units stock mein hain."
                    return f"Yes, {p.name} is in stock in size {size}, with {p.stock} units ready to ship."
                else:
                    if is_hinglish:
                        return f"Maaf kijiye, {p.name} mein size {size} abhi available nahi hai. Isme available sizes {', '.join(str(s) for s in p.sizes)} hain."
                    return f"Sorry, {p.name} is currently not available in size {size}. Available sizes are {', '.join(str(s) for s in p.sizes)}."

        # 4. Product Comparison
        if intent == "product_comparison" and len(products) >= 2:
            p1, p2 = products[0], products[1]
            diff = abs(p1.price - p2.price)
            cheaper = p1.name if p1.price < p2.price else p2.name
            if is_hinglish:
                return f"{p1.name} ₹{p1.price:,} mein hai aur {p2.name} ₹{p2.price:,} mein. {cheaper} ₹{diff:,} sasta hai aur rating {max(p1.rating, p2.rating)} hai. Kya aap inka detailed comparison dekhna chahte hain?"
            return f"{p1.name} is priced at ₹{p1.price:,}, while {p2.name} is ₹{p2.price:,}. {cheaper} is ₹{diff:,} more affordable. Which feature matters more to you?"

        # 5. RAG Answer
        if (intent == "product_details" or "best" in query.lower() or "battery" in query.lower() or "noise" in query.lower()) and rag_context:
            top_p = products[0] if products else None
            if top_p:
                feat = top_p.features[0] if top_p.features else top_p.description[:80]
                if is_hinglish:
                    return f"Verified specs ke anusar, {top_p.name} ₹{top_p.price:,} mein best choice hai. Isme {feat} feature milta hai."
                return f"Based on verified specifications, {top_p.name} at ₹{top_p.price:,} is the best option. It features {feat}."

        # 6. Default Product Search / Recommendation
        if count == 1:
            p = products[0]
            if is_hinglish:
                return f"Mujhe {p.name} mila hai ₹{p.price:,} mein, rating {p.rating} ke saath. Kya aap iske features janna chahenge?"
            return f"I found {p.name} for ₹{p.price:,} with a {p.rating} star rating. Would you like to hear its key features?"
        else:
            p1 = products[0]
            p2 = products[1]
            if is_hinglish:
                return f"Maine aapke liye {count} options dhundhe hain. Top options hain {p1.name} ₹{p1.price:,} mein aur {p2.name} ₹{p2.price:,} mein. Kya aap dono compare karna chahte hain?"
            return f"I found {count} options for you. The top two are {p1.name} at ₹{p1.price:,} and {p2.name} at ₹{p2.price:,}. Would you like me to compare them?"

llm_service = LLMService()
