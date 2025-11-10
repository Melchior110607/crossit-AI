"""
Listings API (SUPABASE VERSION)
Manage product listings across marketplaces
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.core.security import get_current_user
from app.core.supabase import supabase_admin
from app.models.user import User
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_listings(
    marketplace_name: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all listings for the current user with optional filters"""
    query = supabase_admin.table("listings").select(
        "*, products!inner(user_id)"
    ).eq("products.user_id", current_user.id)
    
    if marketplace_name:
        query = query.eq("marketplace_name", marketplace_name)
    
    if status_filter:
        query = query.eq("status", status_filter)
    
    response = query.execute()
    return response.data


@router.get("/{listing_id}", response_model=dict)
async def get_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific listing by ID"""
    response = supabase_admin.table("listings").select(
        "*, products!inner(user_id)"
    ).eq("id", listing_id).eq("products.user_id", current_user.id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    return response.data[0]


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: ListingCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new listing for a product"""
    # Verify product exists and belongs to user
    product_response = supabase_admin.table("products").select("*").eq(
        "id", listing_data.product_id
    ).eq("user_id", current_user.id).execute()
    
    if not product_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if listing already exists for this product and marketplace
    existing = supabase_admin.table("listings").select("*").eq(
        "product_id", listing_data.product_id
    ).eq("marketplace_name", listing_data.marketplace_name).execute()
    
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Listing already exists for {listing_data.marketplace_name}"
        )
    
    # Create listing
    listing_dict = listing_data.dict()
    listing_dict["created_at"] = datetime.now().isoformat()
    listing_dict["updated_at"] = datetime.now().isoformat()
    
    response = supabase_admin.table("listings").insert(listing_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create listing"
        )
    
    # TODO: Trigger async task to publish to marketplace
    
    return response.data[0]


@router.patch("/{listing_id}", response_model=dict)
async def update_listing(
    listing_id: str,
    listing_data: ListingUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a listing"""
    # Verify listing exists and belongs to user
    listing_response = supabase_admin.table("listings").select(
        "*, products!inner(user_id)"
    ).eq("id", listing_id).eq("products.user_id", current_user.id).execute()
    
    if not listing_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Update fields
    update_data = listing_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    response = supabase_admin.table("listings").update(update_data).eq(
        "id", listing_id
    ).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update listing"
        )
    
    return response.data[0]


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a listing"""
    # Verify listing exists and belongs to user
    listing_response = supabase_admin.table("listings").select(
        "*, products!inner(user_id)"
    ).eq("id", listing_id).eq("products.user_id", current_user.id).execute()
    
    if not listing_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # TODO: Trigger async task to delete from marketplace
    
    response = supabase_admin.table("listings").delete().eq("id", listing_id).execute()
    
    return None
