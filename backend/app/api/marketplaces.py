from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.marketplace_connection import MarketplaceConnection

router = APIRouter()

# List of supported marketplaces
MARKETPLACES = [
    {"name": "amazon", "display_name": "Amazon", "description": "Amazon SP-API"},
    {"name": "ebay", "display_name": "eBay", "description": "eBay Marketplace"},
    {"name": "etsy", "display_name": "Etsy", "description": "Etsy Marketplace"},
    {"name": "bol", "display_name": "bol.com", "description": "bol.com Marketplace"},
    {"name": "allegro", "display_name": "Allegro", "description": "Allegro Marketplace"},
    {"name": "kaufland", "display_name": "Kaufland", "description": "Kaufland Global Marketplace"},
    {"name": "onbuy", "display_name": "OnBuy", "description": "OnBuy Marketplace"},
    {"name": "wish", "display_name": "Wish", "description": "Wish Marketplace"},
    {"name": "joom", "display_name": "Joom", "description": "Joom Marketplace"},
    {"name": "zalando", "display_name": "Zalando", "description": "Zalando zDirect"},
    {"name": "aboutyou", "display_name": "ABOUT YOU", "description": "ABOUT YOU Marketplace"},
    {"name": "otto", "display_name": "OTTO Market", "description": "OTTO Market"},
    {"name": "cdiscount", "display_name": "Cdiscount", "description": "Cdiscount Octopia"},
    {"name": "fnac_darty", "display_name": "Fnac Darty", "description": "Fnac Darty Marketplace"},
    {"name": "vinted", "display_name": "Vinted Pro", "description": "Vinted Pro"},
    {"name": "stockx", "display_name": "StockX", "description": "StockX Marketplace"},
    {"name": "shopify", "display_name": "Shopify", "description": "Shopify Store"},
    {"name": "la_redoute", "display_name": "La Redoute", "description": "La Redoute (Mirakl)"},
    {"name": "galeries_lafayette", "display_name": "Galeries Lafayette", "description": "Galeries Lafayette (Mirakl)"},
    {"name": "asos", "display_name": "ASOS", "description": "ASOS Marketplace (Mirakl)"},
]


@router.get("/")
def get_marketplaces():
    """Get list of all supported marketplaces"""
    return {
        "marketplaces": MARKETPLACES,
        "total": len(MARKETPLACES)
    }


@router.get("/connected")
def get_connected_marketplaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of connected marketplaces for current user"""
    connections = db.query(MarketplaceConnection).filter(
        MarketplaceConnection.user_id == current_user.id,
        MarketplaceConnection.is_active == True
    ).all()
    
    connected_marketplaces = []
    for conn in connections:
        marketplace_info = next(
            (m for m in MARKETPLACES if m["name"] == conn.marketplace_name),
            None
        )
        if marketplace_info:
            connected_marketplaces.append({
                **marketplace_info,
                "connection_id": conn.id,
                "connected_at": conn.created_at,
                "last_synced_at": conn.last_synced_at
            })
    
    return {
        "connected_marketplaces": connected_marketplaces,
        "total": len(connected_marketplaces)
    }


@router.post("/{marketplace_name}/connect")
def connect_marketplace(
    marketplace_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate OAuth connection to a marketplace"""
    # Verify marketplace exists
    marketplace = next((m for m in MARKETPLACES if m["name"] == marketplace_name), None)
    if not marketplace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace not found"
        )
    
    # Check if already connected
    existing_connection = db.query(MarketplaceConnection).filter(
        MarketplaceConnection.user_id == current_user.id,
        MarketplaceConnection.marketplace_name == marketplace_name
    ).first()
    
    if existing_connection and existing_connection.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Already connected to {marketplace['display_name']}"
        )
    
    # TODO: Implement OAuth flow for each marketplace
    # For now, return OAuth URL placeholder
    
    return {
        "message": f"OAuth flow for {marketplace['display_name']} not yet implemented",
        "marketplace": marketplace,
        "oauth_url": f"https://oauth.{marketplace_name}.com/authorize?client_id=YOUR_CLIENT_ID"
    }


@router.get("/{marketplace_name}/callback")
def marketplace_callback(
    marketplace_name: str,
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle OAuth callback from marketplace"""
    # TODO: Implement OAuth callback handling
    # Exchange code for access token
    # Store connection in database
    
    return {
        "message": f"OAuth callback for {marketplace_name} not yet implemented",
        "code": code
    }


@router.delete("/{marketplace_name}/disconnect", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_marketplace(
    marketplace_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect from a marketplace"""
    connection = db.query(MarketplaceConnection).filter(
        MarketplaceConnection.user_id == current_user.id,
        MarketplaceConnection.marketplace_name == marketplace_name
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marketplace connection not found"
        )
    
    # Mark as inactive instead of deleting
    connection.is_active = False
    db.commit()
    
    return None

