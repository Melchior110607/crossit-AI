from typing import Dict, List, Optional, Any
from app.integrations.base_connector import BaseMarketplaceConnector
import base64


class KauflandConnector(BaseMarketplaceConnector):
    """
    Kaufland.de Seller API connector
    Documentation: https://sellerapi.kaufland.com/
    Uses API Key authentication (Basic Auth)
    """
    
    BASE_URL = "https://sellerapi.kaufland.com/v2"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """
        Kaufland uses API Key (Basic Auth) - no OAuth flow
        Just return success if credentials are present
        """
        client_key = self.config.get("client_key")
        secret_key = self.config.get("secret_key")
        
        if not client_key or not secret_key:
            raise Exception("Kaufland client_key and secret_key are required")
        
        return {
            "auth_type": "api_key",
            "marketplace": "kaufland",
            "message": "Kaufland uses API Key authentication. Store credentials securely."
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        """
        Not applicable for Kaufland (API Key auth)
        """
        return {
            "access_token": self.config.get("client_key"),
            "refresh_token": "",
            "expires_at": None  # API keys don't expire
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Not applicable for Kaufland (API Key doesn't expire)
        """
        return {
            "access_token": self.config.get("client_key"),
            "refresh_token": "",
            "expires_at": None
        }
    
    def _get_auth_header(self) -> Dict[str, str]:
        """Generate Basic Auth header for Kaufland"""
        client_key = self.config.get("client_key")
        secret_key = self.config.get("secret_key")
        
        credentials = f"{client_key}:{secret_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_listing(self, product_data: Dict, access_token: str = None) -> Dict[str, Any]:
        """
        Create Kaufland product listing
        """
        headers = self._get_auth_header()
        
        # Kaufland requires product to be in their catalog first
        # Then create a unit (listing)
        
        unit_data = {
            "ean": product_data.get("ean") or product_data.get("sku"),  # EAN is required
            "condition": product_data.get("condition", "new"),
            "listing_price": int(product_data.get("price") * 100),  # Price in cents
            "minimum_price": int(product_data.get("price") * 0.9 * 100),  # 10% lower
            "amount": product_data.get("quantity", 1),
            "note": product_data.get("description", "")[:500],  # Max 500 chars
            "fulfillment_type": "shipped_by_seller"  # or "fulfilled_by_kaufland"
        }
        
        url = f"{self.BASE_URL}/units"
        
        response = self._make_request("POST", url, headers=headers, json_data=unit_data)
        result = response.json()
        
        unit_id = result.get("id_unit")
        
        return {
            "marketplace_listing_id": str(unit_id),
            "url": f"https://www.kaufland.de/product/{unit_id}",
            "status": "active"
        }
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str = None) -> Dict[str, Any]:
        """
        Update Kaufland listing
        """
        headers = self._get_auth_header()
        
        update_data = {
            "listing_price": int(product_data.get("price") * 100) if product_data.get("price") else None,
            "amount": product_data.get("quantity"),
            "note": product_data.get("description", "")[:500]
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        url = f"{self.BASE_URL}/units/{listing_id}"
        
        response = self._make_request("PATCH", url, headers=headers, json_data=update_data)
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str = None) -> bool:
        """
        Delete Kaufland listing (set amount to 0)
        """
        headers = self._get_auth_header()
        
        # Kaufland doesn't have delete - just set amount to 0
        update_data = {"amount": 0}
        
        url = f"{self.BASE_URL}/units/{listing_id}"
        
        response = self._make_request("PATCH", url, headers=headers, json_data=update_data)
        return response.status_code == 200
    
    def get_listings(self, access_token: str = None, **filters) -> List[Dict]:
        """
        Get all Kaufland units (listings)
        """
        headers = self._get_auth_header()
        
        url = f"{self.BASE_URL}/units"
        
        params = {
            "limit": filters.get("limit", 100),
            "offset": filters.get("offset", 0)
        }
        
        response = self._make_request("GET", url, headers=headers, params=params)
        return response.json().get("data", [])
    
    def get_listing_details(self, listing_id: str, access_token: str = None) -> Dict[str, Any]:
        """
        Get Kaufland unit details
        """
        headers = self._get_auth_header()
        
        url = f"{self.BASE_URL}/units/{listing_id}"
        
        response = self._make_request("GET", url, headers=headers)
        return response.json()
    
    def get_inventory(self, access_token: str = None) -> List[Dict]:
        """
        Get Kaufland inventory (same as get_listings)
        """
        return self.get_listings(access_token)
    
    def update_inventory(self, listing_id: str, quantity: int, access_token: str = None) -> Dict[str, Any]:
        """
        Update Kaufland inventory quantity
        """
        headers = self._get_auth_header()
        
        update_data = {"amount": quantity}
        
        url = f"{self.BASE_URL}/units/{listing_id}"
        
        response = self._make_request("PATCH", url, headers=headers, json_data=update_data)
        return response.json()
    
    def get_orders(self, access_token: str = None, **filters) -> List[Dict]:
        """
        Get Kaufland orders
        """
        headers = self._get_auth_header()
        
        url = f"{self.BASE_URL}/orders"
        
        params = {
            "limit": filters.get("limit", 100),
            "fulfillment_type": filters.get("fulfillment_type", "shipped_by_seller"),
            "ts_created_from_iso": filters.get("created_after")
        }
        
        response = self._make_request("GET", url, headers=headers, params=params)
        return response.json().get("data", [])
    
    def setup_webhook(self, callback_url: str, access_token: str = None) -> Dict[str, Any]:
        """
        Setup Kaufland webhook
        Kaufland uses push notifications for orders
        """
        headers = self._get_auth_header()
        
        webhook_data = {
            "event_type": "order",
            "callback_url": callback_url,
            "is_active": True
        }
        
        url = f"{self.BASE_URL}/webhooks"
        
        try:
            response = self._make_request("POST", url, headers=headers, json_data=webhook_data)
            return response.json()
        except Exception as e:
            return {
                "message": "Kaufland webhook setup - check API documentation",
                "error": str(e)
            }
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify Kaufland webhook signature
        """
        # Kaufland webhook verification - implement based on docs
        return True

