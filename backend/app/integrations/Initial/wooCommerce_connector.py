from typing import Dict, List, Optional, Any
from app.integrations.base_connector import BaseMarketplaceConnector
import base64


class WooCommerceConnector(BaseMarketplaceConnector):
    """
    WooCommerce REST API connector
    Documentation: https://woocommerce.github.io/woocommerce-rest-api-docs/
    Uses Consumer Key + Consumer Secret (Basic Auth)
    """
    
    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.store_url = config.get("store_url", "")  # e.g., https://mystore.com
        self.BASE_URL = f"{self.store_url}/wp-json/wc/v3"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """
        WooCommerce uses Consumer Key/Secret (no OAuth flow needed)
        """
        consumer_key = self.config.get("consumer_key")
        consumer_secret = self.config.get("consumer_secret")
        
        if not consumer_key or not consumer_secret:
            raise Exception("WooCommerce consumer_key and consumer_secret are required")
        
        return {
            "auth_type": "api_key",
            "marketplace": "woocommerce",
            "store_url": self.store_url,
            "message": "WooCommerce uses Consumer Key/Secret authentication"
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        """
        Not applicable for WooCommerce (uses consumer key/secret)
        """
        return {
            "access_token": self.config.get("consumer_key"),
            "refresh_token": "",
            "expires_at": None
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Not applicable (credentials don't expire)
        """
        return {
            "access_token": self.config.get("consumer_key"),
            "refresh_token": "",
            "expires_at": None
        }
    
    def _get_auth(self) -> tuple:
        """Get Basic Auth tuple for requests"""
        return (
            self.config.get("consumer_key"),
            self.config.get("consumer_secret")
        )
    
    def create_listing(self, product_data: Dict, access_token: str = None) -> Dict[str, Any]:
        """
        Create WooCommerce product
        """
        product = {
            "name": product_data.get("title"),
            "type": "simple",
            "regular_price": str(product_data.get("price")),
            "description": product_data.get("description", ""),
            "short_description": product_data.get("short_description", ""),
            "sku": product_data.get("sku"),
            "manage_stock": True,
            "stock_quantity": product_data.get("quantity", 1),
            "stock_status": "instock" if product_data.get("quantity", 0) > 0 else "outofstock",
            "categories": [
                {"name": product_data.get("category", "Uncategorized")}
            ],
            "images": [
                {"src": img} for img in product_data.get("images", [])
            ],
            "weight": str(product_data.get("weight", 0)),
            "status": "publish"  # or "draft"
        }
        
        url = f"{self.BASE_URL}/products"
        
        response = self._make_request(
            "POST",
            url,
            auth=self._get_auth(),
            json_data=product,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        product_id = result.get("id")
        
        return {
            "marketplace_listing_id": str(product_id),
            "url": result.get("permalink"),
            "status": result.get("status", "publish")
        }
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str = None) -> Dict[str, Any]:
        """
        Update WooCommerce product
        """
        update_data = {}
        
        if product_data.get("title"):
            update_data["name"] = product_data["title"]
        if product_data.get("price"):
            update_data["regular_price"] = str(product_data["price"])
        if product_data.get("description"):
            update_data["description"] = product_data["description"]
        if product_data.get("quantity") is not None:
            update_data["stock_quantity"] = product_data["quantity"]
            update_data["stock_status"] = "instock" if product_data["quantity"] > 0 else "outofstock"
        
        url = f"{self.BASE_URL}/products/{listing_id}"
        
        response = self._make_request(
            "PUT",
            url,
            auth=self._get_auth(),
            json_data=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str = None) -> bool:
        """
        Delete WooCommerce product
        """
        url = f"{self.BASE_URL}/products/{listing_id}"
        
        params = {"force": True}  # Permanently delete (otherwise just trash)
        
        response = self._make_request(
            "DELETE",
            url,
            auth=self._get_auth(),
            params=params
        )
        
        return response.status_code == 200
    
    def get_listings(self, access_token: str = None, **filters) -> List[Dict]:
        """
        Get WooCommerce products
        """
        url = f"{self.BASE_URL}/products"
        
        params = {
            "per_page": filters.get("limit", 100),
            "page": filters.get("page", 1),
            "status": filters.get("status", "any"),
            "orderby": "date",
            "order": "desc"
        }
        
        if filters.get("search"):
            params["search"] = filters["search"]
        
        response = self._make_request(
            "GET",
            url,
            auth=self._get_auth(),
            params=params
        )
        
        return response.json()
    
    def get_listing_details(self, listing_id: str, access_token: str = None) -> Dict[str, Any]:
        """
        Get WooCommerce product details
        """
        url = f"{self.BASE_URL}/products/{listing_id}"
        
        response = self._make_request(
            "GET",
            url,
            auth=self._get_auth()
        )
        
        return response.json()
    
    def get_inventory(self, access_token: str = None) -> List[Dict]:
        """
        Get WooCommerce inventory
        """
        products = self.get_listings(access_token)
        
        inventory = []
        for product in products:
            inventory.append({
                "id": product.get("id"),
                "sku": product.get("sku"),
                "name": product.get("name"),
                "stock_quantity": product.get("stock_quantity"),
                "stock_status": product.get("stock_status"),
                "manage_stock": product.get("manage_stock")
            })
        
        return inventory
    
    def update_inventory(self, listing_id: str, quantity: int, access_token: str = None) -> Dict[str, Any]:
        """
        Update WooCommerce product stock
        """
        update_data = {
            "stock_quantity": quantity,
            "stock_status": "instock" if quantity > 0 else "outofstock"
        }
        
        url = f"{self.BASE_URL}/products/{listing_id}"
        
        response = self._make_request(
            "PUT",
            url,
            auth=self._get_auth(),
            json_data=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        return response.json()
    
    def get_orders(self, access_token: str = None, **filters) -> List[Dict]:
        """
        Get WooCommerce orders
        """
        url = f"{self.BASE_URL}/orders"
        
        params = {
            "per_page": filters.get("limit", 100),
            "page": filters.get("page", 1),
            "status": filters.get("status", "any"),
            "after": filters.get("created_after")
        }
        
        response = self._make_request(
            "GET",
            url,
            auth=self._get_auth(),
            params=params
        )
        
        return response.json()
    
    def setup_webhook(self, callback_url: str, access_token: str = None) -> Dict[str, Any]:
        """
        Setup WooCommerce webhook
        """
        webhook_data = {
            "name": "CrossIt Order Webhook",
            "topic": "order.created",
            "delivery_url": callback_url,
            "status": "active"
        }
        
        url = f"{self.BASE_URL}/webhooks"
        
        response = self._make_request(
            "POST",
            url,
            auth=self._get_auth(),
            json_data=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        
        return response.json()
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify WooCommerce webhook signature
        WooCommerce uses HMAC-SHA256
        """
        import hmac
        import hashlib
        
        expected_signature = base64.b64encode(
            hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).digest()
        ).decode()
        
        return hmac.compare_digest(signature, expected_signature)

