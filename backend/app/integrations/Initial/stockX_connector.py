from typing import Dict, List, Optional, Any
from app.integrations.base_connector import BaseMarketplaceConnector
import base64


class StockXConnector(BaseMarketplaceConnector):
    """
    StockX Developer API connector
    Documentation: https://developer.stockx.com/portal/
    Uses OAuth 2.0 with JWT tokens
    
    Note: StockX API requires developer portal registration
    Security: Uses PerimeterX for bot detection
    """
    
    BASE_URL = "https://api.stockx.com"
    AUTH_URL = "https://accounts.stockx.com/oauth/authorize"
    TOKEN_URL = "https://accounts.stockx.com/oauth/token"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """
        Initiate StockX OAuth 2.0 Authorization Code Flow
        Documentation: https://developer.stockx.com/portal/authentication/
        Follows: https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow
        """
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        state = kwargs.get("state", "")
        
        if not client_id:
            raise Exception("StockX client_id is required. Register at https://developer.stockx.com/")
        
        # StockX uses standard OAuth 2.0 Authorization Code Flow
        # Scopes: openid (required), profile, email, offline_access (for refresh tokens)
        auth_url = (
            f"{self.AUTH_URL}"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&state={state}"
            f"&scope=openid profile email offline_access"  # Added offline_access for refresh tokens
        )
        
        return {
            "auth_url": auth_url,
            "marketplace": "stockx",
            "note": "StockX uses JWT tokens with PerimeterX security. Requires HTTPS redirect URI."
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        """
        Exchange authorization code for JWT access token
        """
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        redirect_uri = self.config.get("redirect_uri")
        
        # Create Basic Auth header
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        response = self._make_request("POST", self.TOKEN_URL, headers=headers, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),  # JWT token
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": token_data.get("expires_in"),
            "token_type": token_data.get("token_type", "Bearer")
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh StockX JWT access token
        """
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = self._make_request("POST", self.TOKEN_URL, headers=headers, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token", refresh_token),
            "expires_at": token_data.get("expires_in")
        }
    
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """
        Create StockX listing (Ask/Bid)
        Note: StockX is a marketplace with Asks (sell) and Bids (buy)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # StockX listing = "Ask" (seller asking price)
        ask_data = {
            "productId": product_data.get("product_id"),  # Must be StockX product ID
            "amount": product_data.get("price"),  # Price in cents
            "expiresAt": product_data.get("expires_at"),  # ISO 8601 date
            "isAnonymous": product_data.get("anonymous", False)
        }
        
        url = f"{self.BASE_URL}/portfolio/asks"
        
        response = self._make_request("POST", url, headers=headers, json_data=ask_data)
        result = response.json()
        
        return {
            "marketplace_listing_id": str(result.get("id")),
            "url": f"https://stockx.com/product/{result.get('productId')}",
            "status": result.get("status", "active"),
            "type": "ask"  # This is a sell listing
        }
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """
        Update StockX ask (listing)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        update_data = {
            "amount": product_data.get("price"),
            "expiresAt": product_data.get("expires_at")
        }
        
        url = f"{self.BASE_URL}/portfolio/asks/{listing_id}"
        
        response = self._make_request("PATCH", url, headers=headers, json_data=update_data)
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        """
        Delete StockX ask (cancel listing)
        """
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        url = f"{self.BASE_URL}/portfolio/asks/{listing_id}"
        
        response = self._make_request("DELETE", url, headers=headers)
        return response.status_code == 204
    
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        """
        Get StockX portfolio (active asks/listings)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}/portfolio/asks"
        
        params = {
            "status": filters.get("status", "active"),
            "limit": filters.get("limit", 100)
        }
        
        response = self._make_request("GET", url, headers=headers, params=params)
        return response.json().get("asks", [])
    
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get StockX ask details
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}/portfolio/asks/{listing_id}"
        
        response = self._make_request("GET", url, headers=headers)
        return response.json()
    
    def get_inventory(self, access_token: str) -> List[Dict]:
        """
        Get StockX inventory (active asks)
        """
        return self.get_listings(access_token, status="active")
    
    def update_inventory(self, listing_id: str, quantity: int, access_token: str) -> Dict[str, Any]:
        """
        StockX doesn't use traditional inventory
        Each listing is unique (1 item per ask)
        To change quantity, create/delete asks
        """
        return {
            "message": "StockX uses individual asks. Create/delete asks to adjust inventory.",
            "listing_id": listing_id
        }
    
    def get_orders(self, access_token: str, **filters) -> List[Dict]:
        """
        Get StockX sales (completed asks)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}/portfolio/sales"
        
        params = {
            "limit": filters.get("limit", 100),
            "status": filters.get("status", "completed")
        }
        
        response = self._make_request("GET", url, headers=headers, params=params)
        return response.json().get("sales", [])
    
    def search_products(self, query: str, access_token: str) -> List[Dict]:
        """
        Search StockX catalog for products
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}/products/search"
        
        params = {"query": query, "limit": 20}
        
        response = self._make_request("GET", url, headers=headers, params=params)
        return response.json().get("products", [])
    
    def get_product_details(self, product_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get StockX product details (market data, pricing)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}/products/{product_id}"
        
        response = self._make_request("GET", url, headers=headers)
        return response.json()
    
    def get_market_data(self, product_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get market data (last sale, highest bid, lowest ask, sales history)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        url = f"{self.BASE_URL}/products/{product_id}/market"
        
        response = self._make_request("GET", url, headers=headers)
        return response.json()
    
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        """
        Setup StockX webhook (if available)
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        webhook_data = {
            "url": callback_url,
            "events": ["ask.matched", "sale.completed"]
        }
        
        url = f"{self.BASE_URL}/webhooks"
        
        try:
            response = self._make_request("POST", url, headers=headers, json_data=webhook_data)
            return response.json()
        except Exception as e:
            return {
                "message": "StockX webhook setup - check API docs for availability",
                "error": str(e)
            }
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify StockX webhook signature
        """
        import hmac
        import hashlib
        
        expected_signature = base64.b64encode(
            hmac.new(secret.encode(), payload, hashlib.sha256).digest()
        ).decode()
        
        return hmac.compare_digest(signature, expected_signature)

