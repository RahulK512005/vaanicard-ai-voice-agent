from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.product import Product
from app.schemas.product import ProductFilterRequest

class ProductProvider(ABC):
    """
    Abstract ProductProvider interface.
    Allows seamlessly swapping between the Mock catalog and Shopify Storefront API
    without changing any shopping agent or conversational business logic.
    """

    @abstractmethod
    async def search(self, filters: ProductFilterRequest) -> List[Product]:
        """Search products matching structured filters and natural keywords."""
        pass

    @abstractmethod
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        """Fetch a single product by its unique identifier."""
        pass

    @abstractmethod
    async def get_by_ids(self, product_ids: List[str]) -> List[Product]:
        """Fetch multiple products given a list of IDs."""
        pass

    @abstractmethod
    async def get_categories(self) -> List[str]:
        """Return list of available product categories."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Product]:
        """Return full list of products for vector indexing."""
        pass
