from typing import Dict, List, Optional, Any
from app.integrations.base_connector import BaseMarketplaceConnector
import hmac
import hashlib
import base64


class AmazonConnector(BaseMarketplaceConnector):
    """
    Amazon SP-API (Selling Partner API) connector
    Documentation: https://developer-docs.amazon.com/sp-api/
    """
    
    BASE_URL = "https://sellingpartnerapi-na.amazon.com"
    AUTH_URL = "https://sellercentral.amazon.com/apps/authorize/consent"
    TOKEN_URL = "https://api.amazon.com/auth/o2/token"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Initiate Amazon OAuth flow"""
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        state = kwargs.get("state", "")
        
        auth_url = (
            f"{self.AUTH_URL}"
            f"?application_id={client_id}"
            f"&state={state}"
            f"&version=beta"
        )
        
        return {
            "auth_url": auth_url,
            "marketplace": "amazon"
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        """Exchange authorization code for access token"""
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        redirect_uri = self.config.get("redirect_uri")
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        
        response = self._make_request("POST", self.TOKEN_URL, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": token_data.get("expires_in"),  # Convert to datetime
            "token_type": token_data.get("token_type")
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh Amazon access token"""
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }
        
        response = self._make_request("POST", self.TOKEN_URL, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": token_data.get("expires_in")
        }
    
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """Create Amazon listing"""
        headers = {
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        }
        
        # Transform product data to Amazon format
        listing_data = self._format_amazon_listing(product_data)
        
        url = f"{self.BASE_URL}/listings/2021-08-01/items/{self.config.get('seller_id')}/{product_data.get('sku')}"
        
        response = self._make_request("PUT", url, headers=headers, json_data=listing_data)
        result = response.json()
        
        return {
            "marketplace_listing_id": result.get("sku"),
            "url": f"https://www.amazon.com/dp/{result.get('asin')}",
            "status": "active"
        }
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """Update Amazon listing"""
        headers = {
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        }
        
        listing_data = self._format_amazon_listing(product_data)
        url = f"{self.BASE_URL}/listings/2021-08-01/items/{self.config.get('seller_id')}/{listing_id}"
        
        response = self._make_request("PATCH", url, headers=headers, json_data=listing_data)
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        """Delete Amazon listing"""
        headers = {
            "x-amz-access-token": access_token
        }
        
        url = f"{self.BASE_URL}/listings/2021-08-01/items/{self.config.get('seller_id')}/{listing_id}"
        
        response = self._make_request("DELETE", url, headers=headers)
        return response.status_code == 200
    
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        """Get Amazon listings"""
        headers = {
            "x-amz-access-token": access_token
        }
        
        url = f"{self.BASE_URL}/listings/2021-08-01/items/{self.config.get('seller_id')}"
        
        response = self._make_request("GET", url, headers=headers, params=filters)
        return response.json().get("items", [])
    
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        """Get Amazon listing details"""
        headers = {
            "x-amz-access-token": access_token
        }
        
        url = f"{self.BASE_URL}/listings/2021-08-01/items/{self.config.get('seller_id')}/{listing_id}"
        
        response = self._make_request("GET", url, headers=headers)
        return response.json()
    
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        """Setup Amazon webhook subscription"""
        headers = {
            "x-amz-access-token": access_token,
            "Content-Type": "application/json"
        }
        
        subscription_data = {
            "payloadVersion": "1.0",
            "destinationId": callback_url
        }
        
        url = f"{self.BASE_URL}/notifications/v1/subscriptions/ORDER_STATUS_CHANGE"
        
        response = self._make_request("POST", url, headers=headers, json_data=subscription_data)
        return response.json()
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Amazon webhook signature"""
        expected_signature = base64.b64encode(
            hmac.new(secret.encode(), payload, hashlib.sha256).digest()
        ).decode()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _format_amazon_listing(self, product_data: Dict) -> Dict:
        """Transform product data to Amazon listing format"""
        return {
            "productType": "PRODUCT",
            "requirements": "LISTING",
            "attributes": {
                "condition_type": [{"value": product_data.get("condition", "new_new")}],
                "item_name": [{"value": product_data.get("title"), "language_tag": "en_US"}],
                "description": [{"value": product_data.get("description"), "language_tag": "en_US"}],
                "bullet_point": [{"value": point, "language_tag": "en_US"} 
                                for point in product_data.get("bullet_points", [])],
                "brand": [{"value": product_data.get("brand", "Generic")}],
                "main_product_image_locator": [{"media_location": product_data.get("images", [])[0]}] 
                    if product_data.get("images") else [],
                "other_product_image_locator": [{"media_location": img} 
                                               for img in product_data.get("images", [])[1:]],
                "list_price": [{
                    "currency": "USD",
                    "value_with_tax": product_data.get("price")
                }]
            }
        }

