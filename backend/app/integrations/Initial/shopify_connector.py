from typing import Dict, List, Any
from app.integrations.base_connector import BaseMarketplaceConnector
import hmac
import hashlib
import base64


class ShopifyConnector(BaseMarketplaceConnector):
    """Shopify Admin API connector - https://shopify.dev"""
    
    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.shop_domain = config.get("shop_domain", "")
        self.BASE_URL = f"https://{self.shop_domain}/admin/api/2024-01"
    
    AUTH_URL_TEMPLATE = "https://{shop}/admin/oauth/authorize"
    TOKEN_URL_TEMPLATE = "https://{shop}/admin/oauth/access_token"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        shop = self.shop_domain
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        scopes = "read_products,write_products,read_orders"
        
        return {
            "auth_url": f"https://{shop}/admin/oauth/authorize?client_id={client_id}&scope={scopes}&redirect_uri={redirect_uri}",
            "marketplace": "shopify"
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        shop = self.shop_domain
        data = {
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret"),
            "code": code
        }
        
        response = self._make_request("POST", f"https://{shop}/admin/oauth/access_token", json_data=data)
        token_data = response.json()
        
        return {"access_token": token_data.get("access_token"), "refresh_token": "", "expires_at": None}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        # Shopify access tokens don't expire
        return {"access_token": refresh_token, "refresh_token": refresh_token, "expires_at": None}
    
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}
        
        product = {
            "product": {
                "title": product_data.get("title"),
                "body_html": product_data.get("description"),
                "vendor": product_data.get("brand", "Unknown"),
                "product_type": product_data.get("category", ""),
                "variants": [{
                    "price": str(product_data.get("price")),
                    "sku": product_data.get("sku"),
                    "inventory_quantity": product_data.get("quantity", 1),
                    "weight": product_data.get("weight"),
                    "weight_unit": "kg"
                }],
                "images": [{"src": img} for img in product_data.get("images", [])]
            }
        }

    
        
        response = self._make_request("POST", f"{self.BASE_URL}/products.json", headers=headers, json_data=product)
        result = response.json().get("product", {})
        
        return {
            "marketplace_listing_id": str(result.get("id")),
            "url": f"https://{self.shop_domain}/products/{result.get('handle')}",
            "status": "active" if result.get("status") == "active" else "draft"
        }
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}
        
        product = {"product": {"title": product_data.get("title"), "body_html": product_data.get("description")}}
        
        response = self._make_request("PUT", f"{self.BASE_URL}/products/{listing_id}.json", headers=headers, json_data=product)
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        headers = {"X-Shopify-Access-Token": access_token}
        response = self._make_request("DELETE", f"{self.BASE_URL}/products/{listing_id}.json", headers=headers)
        return response.status_code == 200
    
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        headers = {"X-Shopify-Access-Token": access_token}
        response = self._make_request("GET", f"{self.BASE_URL}/products.json", headers=headers, params=filters)
        return response.json().get("products", [])
    
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        headers = {"X-Shopify-Access-Token": access_token}
        response = self._make_request("GET", f"{self.BASE_URL}/products/{listing_id}.json", headers=headers)
        return response.json().get("product", {})
    
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}
        
        webhook_data = {
            "webhook": {
                "topic": "orders/create",
                "address": callback_url,
                "format": "json"
            }
        }
        
        response = self._make_request("POST", f"{self.BASE_URL}/webhooks.json", headers=headers, json_data=webhook_data)
        return response.json()
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        computed_hmac = base64.b64encode(hmac.new(secret.encode(), payload, hashlib.sha256).digest()).decode()
        return hmac.compare_digest(computed_hmac, signature)
    
    def get_inventory(self, access_token: str, **filters) -> List[Dict]:
        """Get Shopify inventory levels across all locations"""
        headers = {"X-Shopify-Access-Token": access_token}
        
        # First get all inventory items
        response = self._make_request("GET", f"{self.BASE_URL}/inventory_items.json", headers=headers)
        inventory_items = response.json().get("inventory_items", [])
        
        # Get inventory levels for each item
        inventory_data = []
        for item in inventory_items:
            item_id = item.get("id")
            levels_response = self._make_request(
                "GET", 
                f"{self.BASE_URL}/inventory_levels.json?inventory_item_ids={item_id}", 
                headers=headers
            )
            levels = levels_response.json().get("inventory_levels", [])
            
            inventory_data.append({
                "inventory_item_id": item_id,
                "sku": item.get("sku"),
                "levels": levels
            })
        
        return inventory_data
    
    def update_inventory(self, inventory_item_id: str, quantity: int, access_token: str, location_id: str = None) -> Dict[str, Any]:
        """Update Shopify inventory quantity"""
        headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}
        
        # If no location specified, get the first location
        if not location_id:
            locations_response = self._make_request("GET", f"{self.BASE_URL}/locations.json", headers=headers)
            locations = locations_response.json().get("locations", [])
            if locations:
                location_id = locations[0].get("id")
        
        # Set inventory level
        inventory_data = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": quantity
        }
        
        response = self._make_request(
            "POST", 
            f"{self.BASE_URL}/inventory_levels/set.json", 
            headers=headers, 
            json_data=inventory_data
        )
        
        return response.json()
    
    def get_orders(self, access_token: str, **filters) -> List[Dict]:
        """Get Shopify orders"""
        headers = {"X-Shopify-Access-Token": access_token}
        
        params = {
            "status": filters.get("status", "any"),
            "limit": filters.get("limit", 50),
            "created_at_min": filters.get("created_after")
        }
        
        response = self._make_request("GET", f"{self.BASE_URL}/orders.json", headers=headers, params=params)
        return response.json().get("orders", [])


