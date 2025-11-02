from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ListingBase(BaseModel):
    marketplace_name: str
    price: float


class ListingCreate(ListingBase):
    product_id: int


class ListingUpdate(BaseModel):
    price: Optional[float] = None
    status: Optional[str] = None


class ListingResponse(ListingBase):
    id: int
    product_id: int
    marketplace_listing_id: Optional[str] = None
    status: str
    url: Optional[str] = None
    last_sync_status: str
    last_error: Optional[str] = None
    created_at: datetime
    synced_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None

    class Config:
        from_attributes = True

