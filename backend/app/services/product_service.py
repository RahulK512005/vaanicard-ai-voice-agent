from typing import List, Optional
from app.core.config import settings
from app.models.product import Product
from app.schemas.product import ProductFilterRequest
from app.services.providers.product_provider import ProductProvider
from app.services.providers.mock_product_provider import MockProductProvider
from app.services.providers.shopify_provider import ShopifyProductProvider

class ProductService:
    def __init__(self):
        self.provider: ProductProvider = self._init_provider()

    def _init_provider(self) -> ProductProvider:
        if settings.PRODUCT_PROVIDER.lower() == "shopify" and settings.SHOPIFY_STORE_DOMAIN:
            return ShopifyProductProvider(
                store_domain=settings.SHOPIFY_STORE_DOMAIN,
                storefront_access_token=settings.SHOPIFY_STOREFRONT_ACCESS_TOKEN
            )
        return MockProductProvider()

    async def search(self, filters: ProductFilterRequest) -> List[Product]:
        return await self.provider.search(filters)

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        return await self.provider.get_by_id(product_id)

    async def get_by_ids(self, product_ids: List[str]) -> List[Product]:
        return await self.provider.get_by_ids(product_ids)

    async def get_categories(self) -> List[str]:
        return await self.provider.get_categories()

    async def get_all(self) -> List[Product]:
        return await self.provider.get_all()

product_service = ProductService()
