from fastapi import APIRouter
from app.schemas.chat import RagQueryRequest, RagQueryResponse
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.prompt_service import prompt_service

router = APIRouter(prefix="/api/rag", tags=["RAG"])

@router.post("/query", response_model=RagQueryResponse)
async def query_rag(req: RagQueryRequest):
    """
    RAG Semantic Retrieval endpoint.
    Performs FAISS vector search across chunked catalog specs and descriptions,
    and returns verified grounded answer.
    """
    chunks = rag_service.search(query=req.query, top_k=req.top_k, category_filter=req.category)
    context_str = rag_service.get_grounded_context_string(req.query, top_k=req.top_k)

    system_prompt = prompt_service.get_rag_prompt()
    answer = await llm_service.generate_voice_response(
        query=req.query,
        intent="product_details",
        retrieved_products=[],
        rag_context=context_str,
        pricing_context="",
        language="en",
        system_prompt=system_prompt
    )

    source_products = list({c["product_name"] for c in chunks})

    return RagQueryResponse(
        query=req.query,
        retrieved_chunks=chunks,
        answer=answer,
        source_products=source_products
    )
