"""
Marketplace configurations for OAuth and API connections
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MarketplaceConfig:
    id: str
    name: str
    auth_type: str  # 'oauth2', 'api_key', 'bearer_token', 'basic_auth'
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    api_base_url: Optional[str] = None
    scopes: Optional[list[str]] = None
    requires_shop_domain: bool = False  # For Shopify-like platforms
    documentation_url: Optional[str] = None
    
    # Additional fields for non-OAuth
    api_key_env_var: Optional[str] = None
    api_secret_env_var: Optional[str] = None

# Get environment variables
def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)

# ============================================
# MARKETPLACE CONFIGURATIONS
# ============================================

MARKETPLACE_CONFIGS: Dict[str, MarketplaceConfig] = {
    
    # ===== PHASE 1: MVPs (OAuth 2.0 - Easy) =====
    
    "etsy": MarketplaceConfig(
        id="etsy",
        name="Etsy",
        auth_type="oauth2",
        client_id=get_env("ETSY_KEYSTRING"),
        client_secret=get_env("ETSY_SHARED_SECRET"),
        authorization_url="https://www.etsy.com/oauth/connect",
        token_url="https://api.etsy.com/v3/public/oauth/token",
        api_base_url="https://api.etsy.com/v3",
        scopes=["listings_r", "listings_w", "shops_r", "transactions_r"],
        documentation_url="https://developers.etsy.com/documentation/"
    ),
    
    "shopify": MarketplaceConfig(
        id="shopify",
        name="Shopify",
        auth_type="oauth2",
        client_id=get_env("SHOPIFY_API_KEY"),
        client_secret=get_env("SHOPIFY_API_SECRET"),
        authorization_url="https://{shop}.myshopify.com/admin/oauth/authorize",
        token_url="https://{shop}.myshopify.com/admin/oauth/access_token",
        api_base_url="https://{shop}.myshopify.com/admin/api/2024-01",
        scopes=["read_products", "write_products", "read_orders", "write_orders", "read_inventory", "write_inventory"],
        requires_shop_domain=True,
        documentation_url="https://shopify.dev/docs/api/admin-rest"
    ),
    
    "ebay": MarketplaceConfig(
        id="ebay",
        name="eBay",
        auth_type="oauth2",
        client_id=get_env("EBAY_APP_ID"),
        client_secret=get_env("EBAY_CERT_ID"),
        # URLs change based on EBAY_ENVIRONMENT (SANDBOX or PRODUCTION)
        authorization_url=(
            "https://auth.sandbox.ebay.com/oauth2/authorize" 
            if get_env("EBAY_ENVIRONMENT", "SANDBOX") == "SANDBOX" 
            else "https://auth.ebay.com/oauth2/authorize"
        ),
        token_url=(
            "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
            if get_env("EBAY_ENVIRONMENT", "SANDBOX") == "SANDBOX"
            else "https://api.ebay.com/identity/v1/oauth2/token"
        ),
        api_base_url=(
            "https://api.sandbox.ebay.com"
            if get_env("EBAY_ENVIRONMENT", "SANDBOX") == "SANDBOX"
            else "https://api.ebay.com"
        ),
        # eBay OAuth scopes - Complete set for full marketplace integration
        scopes=[
            "https://api.ebay.com/oauth/api_scope",  # Base scope (REQUIRED)
            "https://api.ebay.com/oauth/api_scope/sell.inventory",
            "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly",
            "https://api.ebay.com/oauth/api_scope/sell.account",
            "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
            "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
            "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
            "https://api.ebay.com/oauth/api_scope/sell.marketing",
            "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly"
        ],
        documentation_url="https://developer.ebay.com/"
    ),
    
    # ===== PHASE 2: European Marketplaces =====
    
    "bol": MarketplaceConfig(
        id="bol",
        name="bol.com",
        auth_type="api_key",
        client_id=get_env("BOL_CLIENT_ID"),
        client_secret=get_env("BOL_CLIENT_SECRET"),
        api_base_url="https://api.bol.com",
        documentation_url="https://api.bol.com/retailer/public/Retailer-API/"
    ),
    
    "allegro": MarketplaceConfig(
        id="allegro",
        name="Allegro",
        auth_type="oauth2",
        client_id=get_env("ALLEGRO_CLIENT_ID"),
        client_secret=get_env("ALLEGRO_CLIENT_SECRET"),
        authorization_url="https://allegro.pl/auth/oauth/authorize",
        token_url="https://allegro.pl/auth/oauth/token",
        api_base_url="https://api.allegro.pl",
        scopes=["allegro:api:sale:offers:read", "allegro:api:sale:offers:write", "allegro:api:orders:read"],
        documentation_url="https://developer.allegro.pl/documentation/"
    ),
    
    "kaufland": MarketplaceConfig(
        id="kaufland",
        name="Kaufland",
        auth_type="api_key",
        api_key_env_var="KAUFLAND_CLIENT_KEY",
        api_secret_env_var="KAUFLAND_SECRET_KEY",
        api_base_url="https://sellerapi.kaufland.com",
        documentation_url="https://sellerapi.kaufland.com/"
    ),
    
    "zalando": MarketplaceConfig(
        id="zalando",
        name="Zalando",
        auth_type="oauth2",
        client_id=get_env("ZALANDO_CLIENT_ID"),
        client_secret=get_env("ZALANDO_CLIENT_SECRET"),
        authorization_url="https://api.zalando.com/oauth/authorize",
        token_url="https://api.zalando.com/oauth/token",
        api_base_url="https://api.zalando.com",
        documentation_url="https://api.zalando.com/"
    ),
    
    "aboutyou": MarketplaceConfig(
        id="aboutyou",
        name="About You",
        auth_type="oauth2",  # API privée
        client_id=get_env("ABOUTYOU_CLIENT_ID"),
        client_secret=get_env("ABOUTYOU_CLIENT_SECRET"),
        api_base_url="https://api.aboutyou.de",  # Hypothetical
        documentation_url="https://aboutyou.de/partners"
    ),
    
    "otto": MarketplaceConfig(
        id="otto",
        name="OTTO Market",
        auth_type="basic_auth",
        client_id=get_env("OTTO_USERNAME"),
        client_secret=get_env("OTTO_PASSWORD"),
        api_base_url="https://api.otto.market",
        documentation_url="https://api.otto.market/docs"
    ),
    
    # ===== PHASE 3: International =====
    
    "wish": MarketplaceConfig(
        id="wish",
        name="Wish",
        auth_type="bearer_token",
        api_key_env_var="WISH_ACCESS_TOKEN",
        api_base_url="https://merchant.wish.com/api/v3",
        documentation_url="https://merchant.wish.com/documentation/api/"
    ),
    
    "joom": MarketplaceConfig(
        id="joom",
        name="Joom",
        auth_type="bearer_token",
        api_key_env_var="JOOM_API_TOKEN",
        api_base_url="https://api-merchant.joom.com",
        documentation_url="https://merchants.joom.com/api/docs"
    ),
    
    "onbuy": MarketplaceConfig(
        id="onbuy",
        name="OnBuy",
        auth_type="api_key",
        api_key_env_var="ONBUY_SECRET_KEY",
        api_secret_env_var="ONBUY_CONSUMER_KEY",
        api_base_url="https://api.onbuy.com",
        documentation_url="https://docs.onbuy.com/"
    ),
    
    "vinted": MarketplaceConfig(
        id="vinted",
        name="Vinted",
        auth_type="oauth2",  # API privée
        client_id=get_env("VINTED_CLIENT_ID"),
        client_secret=get_env("VINTED_CLIENT_SECRET"),
        api_base_url="https://api.vinted.com",  # Hypothetical
        documentation_url="https://www.vinted.fr/pro"
    ),
    
    # ===== PHASE 4: French Marketplaces =====
    
    "cdiscount": MarketplaceConfig(
        id="cdiscount",
        name="Cdiscount",
        auth_type="bearer_token",
        api_key_env_var="CDISCOUNT_API_TOKEN",
        api_base_url="https://api.cdiscount.com",
        documentation_url="https://dev.cdiscount.com/"
    ),
    
    "fnacdarty": MarketplaceConfig(
        id="fnacdarty",
        name="Fnac Darty",
        auth_type="api_key",
        api_key_env_var="FNAC_PARTNER_TOKEN",
        api_secret_env_var="FNAC_SHOP_ID",
        api_base_url="https://api.fnac.com",
        documentation_url="https://developer.fnac.com/"
    ),
    
    "laredoute": MarketplaceConfig(
        id="laredoute",
        name="La Redoute",
        auth_type="api_key",  # API privée
        api_key_env_var="LAREDOUTE_API_KEY",
        api_base_url="https://api.laredoute.fr",  # Hypothetical
        documentation_url="https://www.laredoute.fr/marketplace"
    ),
    
    "galerieslafayette": MarketplaceConfig(
        id="galerieslafayette",
        name="Galeries Lafayette",
        auth_type="api_key",  # API non publique
        api_key_env_var="GL_API_KEY",
        api_base_url="https://api.galerieslafayette.com",  # Hypothetical
        documentation_url="https://www.galerieslafayette.com/"
    ),
    
    # ===== PHASE 5: Specialized =====
    
    "stockx": MarketplaceConfig(
        id="stockx",
        name="StockX",
        auth_type="oauth2",
        client_id=get_env("STOCKX_CLIENT_ID"),
        client_secret=get_env("STOCKX_CLIENT_SECRET"),
        authorization_url="https://accounts.stockx.com/oauth/authorize",
        token_url="https://accounts.stockx.com/oauth/token",
        api_base_url="https://api.stockx.com",
        scopes=["openid", "profile", "email", "offline_access"],  # Added offline_access for refresh tokens
        documentation_url="https://developer.stockx.com/portal/"
    ),
    
    "asos": MarketplaceConfig(
        id="asos",
        name="ASOS Marketplace",
        auth_type="api_key",  # API non publique
        api_key_env_var="ASOS_API_KEY",
        api_base_url="https://api.asos.com",  # Hypothetical
        documentation_url="https://marketplace.asos.com/"
    ),
    
    "woocommerce": MarketplaceConfig(
        id="woocommerce",
        name="WooCommerce",
        auth_type="api_key",  # User provides their own keys (self-hosted)
        api_key_env_var="WOOCOMMERCE_CONSUMER_KEY",  # These are per-user, not global
        api_secret_env_var="WOOCOMMERCE_CONSUMER_SECRET",
        api_base_url="",  # User provides their own domain
        requires_shop_domain=True,  # User must provide their WooCommerce URL
        documentation_url="https://woocommerce.github.io/woocommerce-rest-api-docs/"
    ),
    
    # ===== PHASE 6: Amazon (Most Complex) =====
    
    "amazon": MarketplaceConfig(
        id="amazon",
        name="Amazon SP-API",
        auth_type="oauth2",  # OAuth + AWS Signature
        client_id=get_env("AMAZON_LWA_CLIENT_ID"),
        client_secret=get_env("AMAZON_LWA_CLIENT_SECRET"),
        authorization_url="https://sellercentral.amazon.com/apps/authorize/consent",
        token_url="https://api.amazon.com/auth/o2/token",
        api_base_url="https://sellingpartnerapi-eu.amazon.com",
        documentation_url="https://developer-docs.amazon.com/sp-api/"
    ),
}

def get_marketplace_config(marketplace_id: str) -> Optional[MarketplaceConfig]:
    """Get configuration for a specific marketplace"""
    return MARKETPLACE_CONFIGS.get(marketplace_id)

def get_all_marketplace_configs() -> Dict[str, MarketplaceConfig]:
    """Get all marketplace configurations"""
    return MARKETPLACE_CONFIGS

def get_marketplaces_by_auth_type(auth_type: str) -> Dict[str, MarketplaceConfig]:
    """Get marketplaces filtered by auth type"""
    return {
        id: config for id, config in MARKETPLACE_CONFIGS.items()
        if config.auth_type == auth_type
    }

