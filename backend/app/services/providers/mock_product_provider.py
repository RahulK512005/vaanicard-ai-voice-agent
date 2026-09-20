import json
import os
from typing import List, Optional, Dict
from pathlib import Path
from app.models.product import Product
from app.schemas.product import ProductFilterRequest
from app.services.providers.product_provider import ProductProvider

class MockProductProvider(ProductProvider):
    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            base_dir = Path(__file__).resolve().parent.parent.parent
            data_path = os.path.join(base_dir, "data", "products.json")

        self.data_path = data_path
        self._products: Dict[str, Product] = {}
        self._categories: List[str] = []
        self._load_data()

    def _load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        for item in raw_items:
            product = Product(**item)
            self._products[product.id] = product

        self._categories = sorted(list({p.category for p in self._products.values()}))

    async def get_all(self) -> List[Product]:
        return list(self._products.values())

    async def get_categories(self) -> List[str]:
        return self._categories

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)

    async def get_by_ids(self, product_ids: List[str]) -> List[Product]:
        results = []
        for pid in product_ids:
            if pid in self._products:
                results.append(self._products[pid])
        return results

    async def search(self, filters: ProductFilterRequest) -> List[Product]:
        results = list(self._products.values())

        # Category filter (case-insensitive substring or exact match)
        if filters.category:
            cat_lower = filters.category.lower().strip()
            results = [
                p for p in results
                if cat_lower in p.category.lower() or p.category.lower() in cat_lower
            ]

        # Brand filter
        if filters.brand:
            brand_lower = filters.brand.lower().strip()
            results = [p for p in results if brand_lower in p.brand.lower()]

        # Color filter
        if filters.color:
            color_lower = filters.color.lower().strip()
            results = [p for p in results if color_lower in p.color.lower()]

        # Size filter
        if filters.size is not None:
            size_str = str(filters.size).lower().strip()
            results = [
                p for p in results
                if any(str(s).lower() == size_str or size_str in str(s).lower() for s in p.sizes)
            ]

        # Price range
        if filters.min_price is not None:
            results = [p for p in results if p.price >= filters.min_price]
        if filters.max_price is not None:
            results = [p for p in results if p.price <= filters.max_price]

        # Minimum rating
        if filters.min_rating is not None:
            results = [p for p in results if p.rating >= filters.min_rating]

        # In stock only
        if filters.in_stock_only:
            results = [p for p in results if p.in_stock]

        # Keyword / Query search
        if filters.query:
            q_terms = filters.query.lower().split()
            scored_results = []
            for p in results:
                score = 0
                searchable = f"{p.name} {p.brand} {p.category} {p.description} {' '.join(p.tags)} {' '.join(p.features)}".lower()
                
                # Check for exact whole phrase match
                if filters.query.lower() in searchable:
                    score += 10
                
                # Term matches
                for term in q_terms:
                    if len(term) < 2:
                        continue
                    if term in p.name.lower():
                        score += 5
                    elif term in p.category.lower():
                        score += 4
                    elif term in p.brand.lower():
                        score += 4
                    elif term in [t.lower() for t in p.tags]:
                        score += 3
                    elif term in searchable:
                        score += 1
                
                if score > 0:
                    scored_results.append((score, p))
            
            # Sort by score descending
            scored_results.sort(key=lambda x: x[0], reverse=True)
            results = [p for _, p in scored_results]

        # Sorting
        if filters.sort_by == "price_asc":
            results.sort(key=lambda p: p.price)
        elif filters.sort_by == "price_desc":
            results.sort(key=lambda p: p.price, reverse=True)
        elif filters.sort_by == "rating":
            results.sort(key=lambda p: p.rating, reverse=True)
        elif filters.sort_by == "discount":
            results.sort(key=lambda p: p.discount_percentage, reverse=True)

        # Pagination
        start = filters.offset
        end = filters.offset + filters.limit
        return results[start:end]
