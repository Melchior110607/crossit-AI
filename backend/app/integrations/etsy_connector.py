from typing import Dict, List, Optional, Any
from app.integrations.base_connector import BaseMarketplaceConnector


class EtsyConnector(BaseMarketplaceConnector):
    """
    Etsy Open API v3 connector
    Documentation: https://developer.etsy.com/
    """
    
    BASE_URL = "https://openapi.etsy.com/v3"
    AUTH_URL = "https://www.etsy.com/oauth/connect"
    TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Initiate Etsy OAuth flow"""
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        scopes = "listings_w listings_r"
        state = kwargs.get("state", "")
        
        # Generate code verifier and challenge for PKCE
        code_verifier = kwargs.get("code_verifier", "")  # Should be generated on client
        
        auth_url = (
            f"{self.AUTH_URL}"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )
        
        return {
            "auth_url": auth_url,
            "marketplace": "etsy",
            "code_verifier": code_verifier
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        """Exchange authorization code for access token"""
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        code_verifier = kwargs.get("code_verifier", "")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
            "code_verifier": code_verifier
        }
        
        response = self._make_request("POST", self.TOKEN_URL, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": token_data.get("expires_in"),
            "token_type": token_data.get("token_type")
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh Etsy access token"""
        client_id = self.config.get("client_id")
        
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token
        }
        
        response = self._make_request("POST", self.TOKEN_URL, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": token_data.get("expires_in")
        }
    
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """Create Etsy listing"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "x-api-key": self.config.get("client_id")
        }
        
        shop_id = self.config.get("shop_id")
        url = f"{self.BASE_URL}/application/shops/{shop_id}/listings"
        
        listing_data = self._format_etsy_listing(product_data)
        
        response = self._make_request("POST", url, headers=headers, json_data=listing_data)
        listing = response.json()
        
        # Upload images if provided
        if product_data.get("images"):
            self._upload_listing_images(listing.get("listing_id"), product_data.get("images"), access_token)
        
        return {
            "marketplace_listing_id": str(listing.get("listing_id")),
            "url": listing.get("url"),
            "status": listing.get("state", "active")
        }
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """Update Etsy listing"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "x-api-key": self.config.get("client_id")
        }
        
        shop_id = self.config.get("shop_id")
        url = f"{self.BASE_URL}/application/shops/{shop_id}/listings/{listing_id}"
        
        listing_data = self._format_etsy_listing(product_data)
        
        response = self._make_request("PUT", url, headers=headers, json_data=listing_data)
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        """Delete/deactivate Etsy listing"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.config.get("client_id")
        }
        
        shop_id = self.config.get("shop_id")
        url = f"{self.BASE_URL}/application/shops/{shop_id}/listings/{listing_id}"
        
        response = self._make_request("DELETE", url, headers=headers)
        return response.status_code == 200
    
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        """Get Etsy shop listings"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.config.get("client_id")
        }
        
        shop_id = self.config.get("shop_id")
        url = f"{self.BASE_URL}/application/shops/{shop_id}/listings"
        
        params = {
            "state": filters.get("state", "active"),
            "limit": filters.get("limit", 25)
        }
        
        response = self._make_request("GET", url, headers=headers, params=params)
        return response.json().get("results", [])
    
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        """Get Etsy listing details"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.config.get("client_id")
        }
        
        url = f"{self.BASE_URL}/application/listings/{listing_id}"
        
        response = self._make_request("GET", url, headers=headers)
        return response.json()
    
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        """Setup Etsy webhook - Note: Etsy webhooks are limited"""
        # Etsy has limited webhook support
        return {
            "message": "Etsy webhook support is limited. Consider email parsing fallback.",
            "callback_url": callback_url
        }
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Etsy webhook signature"""
        # Implement Etsy-specific verification if webhooks are available
        return True
    
    def _format_etsy_listing(self, product_data: Dict) -> Dict:
        """Format product data for Etsy listing"""
        return {
            "quantity": product_data.get("quantity", 1),
            "title": product_data.get("title")[:140],  # Etsy has 140 char limit
            "description": product_data.get("description"),
            "price": product_data.get("price"),
            "who_made": "i_did",  # Options: i_did, someone_else, collective
            "when_made": "made_to_order",  # Or specific years
            "taxonomy_id": 1,  # Category ID - should be mapped properly
            "shipping_profile_id": self.config.get("shipping_profile_id"),
            "return_policy_id": self.config.get("return_policy_id"),
            "materials": product_data.get("materials", []),
            "shop_section_id": self.config.get("shop_section_id"),
            "processing_min": 1,
            "processing_max": 3,
            "tags": product_data.get("tags", [])[:13],  # Max 13 tags
            "styles": product_data.get("styles", [])[:2],  # Max 2 styles
            "item_weight": product_data.get("weight"),
            "item_length": product_data.get("dimensions", {}).get("length"),
            "item_width": product_data.get("dimensions", {}).get("width"),
            "item_height": product_data.get("dimensions", {}).get("height"),
            "item_weight_unit": "oz",
            "item_dimensions_unit": "in",
            "is_personalizable": False,
            "is_customizable": False,
            "is_taxable": True,
            "is_supply": False
        }
    
    def _upload_listing_images(self, listing_id: int, image_urls: List[str], access_token: str):
        """Upload images to Etsy listing"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "x-api-key": self.config.get("client_id")
        }
        
        shop_id = self.config.get("shop_id")
        
        for rank, image_url in enumerate(image_urls[:10], start=1):  # Max 10 images
            url = f"{self.BASE_URL}/application/shops/{shop_id}/listings/{listing_id}/images"
            
            data = {
                "image_url": image_url,
                "rank": rank
            }
            
            try:
                self._make_request("POST", url, headers=headers, json_data=data)
            except Exception as e:
                print(f"Failed to upload image {image_url}: {e}")

