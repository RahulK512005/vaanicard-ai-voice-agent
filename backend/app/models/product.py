from typing import List, Optional, Union
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: str
    name: str
    category: str
    brand: str
    description: str
    price: int  # Price in INR
    original_price: int  # Original MRP in INR
    discount_percentage: int
    color: str
    sizes: List[Union[int, str]]
    rating: float
    stock: int
    features: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def discount_amount(self) -> int:
        return max(0, self.original_price - self.price)
