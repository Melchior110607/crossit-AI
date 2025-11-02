from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    condition: Optional[str] = "new"
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = 1
    weight: Optional[float] = None
    dimensions: Optional[Dict] = None
    metadata: Optional[Dict] = None


class ProductCreate(ProductBase):
    images: Optional[List[str]] = []


class ProductUpdate(ProductBase):
    title: Optional[str] = None
    price: Optional[float] = None
    images: Optional[List[str]] = None


class ProductResponse(ProductBase):
    id: int
    user_id: int
    images: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

