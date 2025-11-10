"""
Products API endpoints (using Supabase)
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.core.supabase import supabase_admin

router = APIRouter()

# Pydantic models
class ProductBase(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    category: Optional[str] = None
    brand: Optional[str] = None
    sku: Optional[str] = None
    condition: str = "new"
    quantity: int = 1
    images: Optional[List[str]] = []
    status: str = "draft"

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    status: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    price: Optional[float]
    currency: str
    category: Optional[str]
    brand: Optional[str]
    sku: Optional[str]
    condition: str
    quantity: int
    images: Optional[List[str]]
    status: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

# Temporary mock user_id until auth is integrated
MOCK_USER_ID = "user-123"

@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all products"""
    query = supabase_admin.table("products").select("*")
    
    if status_filter:
        query = query.eq("status", status_filter)
    
    if search:
        query = query.or_(f"title.ilike.%{search}%,sku.ilike.%{search}%")
    
    query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
    
    response = query.execute()
    return response.data

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get a single product"""
    response = supabase_admin.table("products").select("*").eq("id", product_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return response.data[0]

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    """Create a new product"""
    product_data = product.dict()
    
    try:
        response = supabase_admin.table("products").insert(product_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create product")
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product_update: ProductUpdate):
    """Update a product"""
    # Check if product exists
    check_response = supabase_admin.table("products").select("id").eq("id", product_id).execute()
    if not check_response.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update product
    update_data = product_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    response = supabase_admin.table("products").update(update_data).eq("id", product_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update product")
    
    return response.data[0]

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str):
    """Delete a product"""
    response = supabase_admin.table("products").delete().eq("id", product_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return None

@router.get("/products/stats/summary")
async def get_products_stats():
    """Get products statistics"""
    # Get all products
    response = supabase_admin.table("products").select("status,price,quantity").execute()
    products = response.data
    
    stats = {
        "total": len(products),
        "active": len([p for p in products if p.get("status") == "active"]),
        "draft": len([p for p in products if p.get("status") == "draft"]),
        "total_value": sum([p.get("price", 0) * p.get("quantity", 0) for p in products]),
    }
    
    return stats

