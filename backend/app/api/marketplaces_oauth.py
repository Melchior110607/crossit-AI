"""
OAuth endpoints for ALL marketplaces
Generic implementation that works with any marketplace configuration
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
import logging
import os

from app.core.marketplace_config import get_marketplace_config, get_all_marketplace_configs
from app.services.oauth_service import OAuthService, APIKeyService

router = APIRouter()
logger = logging.getLogger(__name__)

# Temporary mock user ID (replace with real auth later)
MOCK_USER_ID = "user-123"

# Base redirect URL - can be overridden by environment variable
BASE_REDIRECT_URL = os.getenv("BASE_REDIRECT_URL", "http://localhost:3000")

# ============================================
# PYDANTIC MODELS
# ============================================

class OAuthInitResponse(BaseModel):
    authorization_url: str
    state: str
    marketplace: str

class OAuthCallbackResponse(BaseModel):
    success: bool
    marketplace: str
    message: str
    connection_id: Optional[str] = None

class APIKeyConnectRequest(BaseModel):
    api_key: str
    api_secret: Optional[str] = None
    shop_domain: Optional[str] = None  # For Shopify-like platforms

class MarketplaceConnectionResponse(BaseModel):
    id: str
    marketplace_id: str
    marketplace_name: str
    status: str
    connected_at: int

# ============================================
# OAUTH ENDPOINTS (For OAuth 2.0 marketplaces)
# ============================================

@router.get("/marketplaces/{marketplace_id}/auth-url", response_model=OAuthInitResponse)
async def get_oauth_authorization_url(
    marketplace_id: str,
    shop_domain: Optional[str] = Query(None, description="Required for Shopify-like platforms"),
    user_id: str = MOCK_USER_ID
):
    """
    Get OAuth authorization URL for any marketplace
    
    Supported marketplaces (OAuth 2.0):
    - etsy, shopify, ebay, allegro, zalando, amazon
    """
    config = get_marketplace_config(marketplace_id)
    
    if not config:
        raise HTTPException(status_code=404, detail=f"Marketplace '{marketplace_id}' not found")
    
    if config.auth_type != "oauth2":
        raise HTTPException(
            status_code=400, 
            detail=f"Marketplace '{marketplace_id}' uses {config.auth_type}, not OAuth 2.0. Use /connect-api-key endpoint instead."
        )
    
    # Check if credentials are configured
    if not config.client_id or not config.client_secret:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth credentials not configured for {marketplace_id}. Please set environment variables."
        )
    
    # Get redirect URI from env or use base URL
    redirect_uri = os.getenv(f"{marketplace_id.upper()}_REDIRECT_URI", 
                             f"{BASE_REDIRECT_URL}/dashboard/marketplaces/callback/{marketplace_id}")
    
    if config.requires_shop_domain and not shop_domain:
        raise HTTPException(
            status_code=400,
            detail=f"{marketplace_id} requires a shop_domain parameter"
        )
    
    # Replace {shop} placeholder for Shopify-like platforms
    auth_url = config.authorization_url
    token_url = config.token_url
    if shop_domain:
        auth_url = auth_url.replace("{shop}", shop_domain)
        token_url = token_url.replace("{shop}", shop_domain)
    
    # Prepare extra parameters for specific marketplaces (if needed)
    extra_params = {}
    # Note: eBay RU_NAME is NOT sent as a parameter, it's just an identifier in the developer portal
    
    # Create OAuth service
    oauth_service = OAuthService(
        marketplace_id=marketplace_id,
        client_id=config.client_id,
        client_secret=config.client_secret,
        authorization_url=auth_url,
        token_url=token_url,
        redirect_uri=redirect_uri,
        scopes=config.scopes,
        extra_params=extra_params
    )
    
    # Generate authorization URL
    result = oauth_service.generate_authorization_url(user_id)
    
    # Debug logging for eBay
    if marketplace_id == "ebay":
        logger.info(f"eBay OAuth URL generated: {result['url']}")
    
    return OAuthInitResponse(
        authorization_url=result["url"],
        state=result["state"],
        marketplace=marketplace_id
    )


@router.get("/marketplaces/{marketplace_id}/callback")
async def oauth_callback(
    marketplace_id: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    shop: Optional[str] = Query(None, description="Shop domain for Shopify"),
    user_id: str = MOCK_USER_ID
):
    """
    OAuth callback endpoint - exchanges code for access token
    This is called directly by OAuth provider, then redirects to frontend
    """
    from fastapi.responses import RedirectResponse
    
    config = get_marketplace_config(marketplace_id)
    
    if not config:
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"http://localhost:3000/dashboard/marketplaces?error=marketplace_not_found",
            status_code=302
        )
    
    if config.auth_type != "oauth2":
        return RedirectResponse(
            url=f"http://localhost:3000/dashboard/marketplaces?error=invalid_auth_type",
            status_code=302
        )
    
    # Get redirect URI from env or use backend URL
    redirect_uri = os.getenv(f"{marketplace_id.upper()}_REDIRECT_URI", 
                             f"http://localhost:8000/api/marketplaces/{marketplace_id}/callback")
    
    # Handle shop domain for Shopify-like platforms
    token_url = config.token_url
    if shop:
        # For Shopify, the 'shop' parameter already includes .myshopify.com
        # So we need to extract just the store name
        shop_name = shop.replace('.myshopify.com', '') if '.myshopify.com' in shop else shop
        token_url = token_url.replace("{shop}", shop_name)
    
    try:
        oauth_service = OAuthService(
            marketplace_id=marketplace_id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            authorization_url=config.authorization_url,
            token_url=token_url,
            redirect_uri=redirect_uri,
            scopes=config.scopes
        )
        
        # Exchange code for token
        tokens = oauth_service.exchange_code_for_token(code, user_id)
        
        logger.info(f"Successfully connected {marketplace_id} for user {user_id}")
        
        # Redirect to frontend with success
        return RedirectResponse(
            url=f"http://localhost:3000/dashboard/marketplaces?success=true&marketplace={marketplace_id}",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"OAuth callback error for {marketplace_id}: {str(e)}")
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"http://localhost:3000/dashboard/marketplaces?error=connection_failed&marketplace={marketplace_id}",
            status_code=302
        )


# ============================================
# API KEY ENDPOINTS (For API Key marketplaces)
# ============================================

@router.post("/marketplaces/{marketplace_id}/connect-api-key", response_model=OAuthCallbackResponse)
async def connect_with_api_key(
    marketplace_id: str,
    request: APIKeyConnectRequest,
    user_id: str = MOCK_USER_ID
):
    """
    Connect marketplace using API Key (not OAuth)
    
    Supported marketplaces:
    - bol, kaufland, otto, wish, joom, onbuy, cdiscount, fnacdarty, etc.
    """
    config = get_marketplace_config(marketplace_id)
    
    if not config:
        raise HTTPException(status_code=404, detail=f"Marketplace '{marketplace_id}' not found")
    
    if config.auth_type == "oauth2":
        raise HTTPException(
            status_code=400,
            detail=f"{marketplace_id} uses OAuth 2.0. Use /auth-url endpoint instead."
        )
    
    try:
        api_key_service = APIKeyService(marketplace_id)
        
        success = api_key_service.store_api_key(
            user_id=user_id,
            api_key=request.api_key,
            api_secret=request.api_secret
        )
        
        if success:
            return OAuthCallbackResponse(
                success=True,
                marketplace=marketplace_id,
                message=f"Successfully connected to {config.name}!",
                connection_id=f"{marketplace_id}-{user_id}"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to store API key")
            
    except Exception as e:
        logger.error(f"API Key connection error for {marketplace_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to {marketplace_id}: {str(e)}"
        )


# ============================================
# DISCONNECT & STATUS ENDPOINTS
# ============================================

@router.post("/marketplaces/{marketplace_id}/disconnect")
async def disconnect_marketplace(
    marketplace_id: str,
    user_id: str = MOCK_USER_ID
):
    """Disconnect from a marketplace"""
    config = get_marketplace_config(marketplace_id)
    
    if not config:
        raise HTTPException(status_code=404, detail=f"Marketplace '{marketplace_id}' not found")
    
    if config.auth_type == "oauth2":
        oauth_service = OAuthService(
            marketplace_id=marketplace_id,
            client_id=config.client_id or "",
            client_secret=config.client_secret or "",
            authorization_url=config.authorization_url or "",
            token_url=config.token_url or "",
            redirect_uri=""
        )
        success = oauth_service.disconnect(user_id)
    else:
        api_key_service = APIKeyService(marketplace_id)
        # For now, just mark as disconnected
        success = True  # TODO: implement disconnect for API keys
    
    if success:
        return {"success": True, "message": f"Disconnected from {config.name}"}
    else:
        raise HTTPException(status_code=404, detail="Connection not found")


@router.get("/marketplaces/connected")
async def get_connected_marketplaces(user_id: str = MOCK_USER_ID):
    """Get all connected marketplaces for a user (SUPABASE VERSION)"""
    from app.core.supabase import supabase_admin
    
    response = supabase_admin.table("marketplace_connections").select(
        "id,marketplace_id,marketplace_name,status,created_at,last_sync_at"
    ).eq("user_id", user_id).eq("status", "active").order("created_at", desc=True).execute()
    
    return {"connections": response.data, "total": len(response.data)}


@router.get("/marketplaces/available")
async def get_available_marketplaces():
    """Get list of all available marketplaces with their config"""
    configs = get_all_marketplace_configs()
    
    marketplaces = []
    for id, config in configs.items():
        # Check if credentials are configured
        is_configured = False
        if config.auth_type == "oauth2":
            is_configured = bool(config.client_id and config.client_secret)
        elif config.auth_type in ["api_key", "bearer_token"]:
            is_configured = bool(config.api_key_env_var)
        
        marketplaces.append({
            "id": id,
            "name": config.name,
            "auth_type": config.auth_type,
            "is_configured": is_configured,
            "requires_shop_domain": config.requires_shop_domain,
            "documentation_url": config.documentation_url
        })
    
    return {"marketplaces": marketplaces, "total": len(marketplaces)}

