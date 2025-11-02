from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.listing import Listing
from app.models.product import Product
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse

router = APIRouter()


@router.get("/", response_model=List[ListingResponse])
def get_listings(
    marketplace_name: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all listings for the current user with optional filters"""
    query = db.query(Listing).join(Product).filter(Product.user_id == current_user.id)
    
    if marketplace_name:
        query = query.filter(Listing.marketplace_name == marketplace_name)
    
    if status:
        query = query.filter(Listing.status == status)
    
    listings = query.all()
    return listings


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific listing by ID"""
    listing = db.query(Listing).join(Product).filter(
        Listing.id == listing_id,
        Product.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    return listing


@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    listing_data: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new listing for a product"""
    # Verify product exists and belongs to user
    product = db.query(Product).filter(
        Product.id == listing_data.product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if listing already exists for this product and marketplace
    existing_listing = db.query(Listing).filter(
        Listing.product_id == listing_data.product_id,
        Listing.marketplace_name == listing_data.marketplace_name
    ).first()
    
    if existing_listing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Listing already exists for {listing_data.marketplace_name}"
        )
    
    # Create listing
    new_listing = Listing(**listing_data.model_dump())
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    
    # TODO: Trigger async task to publish to marketplace
    
    return new_listing


@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    listing_data: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a listing"""
    listing = db.query(Listing).join(Product).filter(
        Listing.id == listing_id,
        Product.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Update fields
    update_data = listing_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)
    
    db.commit()
    db.refresh(listing)
    
    return listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a listing"""
    listing = db.query(Listing).join(Product).filter(
        Listing.id == listing_id,
        Product.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # TODO: Trigger async task to delete from marketplace
    
    db.delete(listing)
    db.commit()
    
    return None

