from fastapi import APIRouter
from app.core.config import settings
from app.services.product_service import product_service
from app.services.rag_service import rag_service

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    products = await product_service.get_all()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "catalog_provider": settings.PRODUCT_PROVIDER,
        "products_count": len(products),
        "rag_ready": rag_service._is_ready,
        "rag_chunks_count": len(rag_service.chunks)
    }
