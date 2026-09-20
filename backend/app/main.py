import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.product_service import product_service
from app.services.rag_service import rag_service
from app.api.routes import health, products, pricing, compare, recommend, rag, conversation, chat

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("vaanicart")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing VaaniCart AI backend services...")
    # Load all products and build FAISS RAG index
    all_products = await product_service.get_all()
    logger.info("Loaded %d products into memory.", len(all_products))
    rag_service.build_index(all_products)
    logger.info("VaaniCart AI is ready to receive requests!")
    yield
    logger.info("VaaniCart AI shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack AI Voice Shopping Assistant backend for Indian e-commerce.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration - Allow localhost, 127.0.0.1, all Vercel domains and preview URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://vaanicard-ai-voice-agent.vercel.app"
    ],
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "health": "/health",
        "docs": "/docs"
    }

# Include API Routers
app.include_router(health.router)
app.include_router(products.router)
app.include_router(pricing.router)
app.include_router(compare.router)
app.include_router(recommend.router)
app.include_router(rag.router)
app.include_router(conversation.router)
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
