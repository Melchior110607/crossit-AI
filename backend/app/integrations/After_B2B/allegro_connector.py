from typing import Dict, List, Any
from app.integrations.base_connector import BaseMarketplaceConnector
import base64


class AllegroConnector(BaseMarketplaceConnector):
    """Allegro REST API connector - https://developer.allegro.pl"""
    
    BASE_URL = "https://api.allegro.pl"
    AUTH_URL = "https://allegro.pl/auth/oauth/authorize"
    TOKEN_URL = "https://allegro.pl/auth/oauth/token"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        
        return {
            "auth_url": f"{self.AUTH_URL}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}",
            "marketplace": "allegro"
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "authorization_code", "code": code, "redirect_uri": self.config.get("redirect_uri")}
        
        response = self._make_request("POST", self.TOKEN_URL, headers=headers, data=data)
        token_data = response.json()
        
        return {"access_token": token_data.get("access_token"), "refresh_token": token_data.get("refresh_token"), "expires_at": token_data.get("expires_in")}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        client_id = self.config.get("client_id")
        client_secret = self.config.get("client_secret")
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        
        response = self._make_request("POST", self.TOKEN_URL, headers=headers, data=data)
        token_data = response.json()
        return {"access_token": token_data.get("access_token"), "refresh_token": refresh_token, "expires_at": token_data.get("expires_in")}
    
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/vnd.allegro.public.v1+json"}
        
        listing_data = {
            "name": product_data.get("title"),
            "category": {"id": "1"},  # Category mapping needed
            "sellingMode": {"format": "BUY_NOW", "price": {"amount": str(product_data.get("price")), "currency": "PLN"}},
            "stock": {"available": product_data.get("quantity", 1)},
            "description": {"sections": [{"items": [{"type": "TEXT", "content": product_data.get("description")}]}]},
            "images": [{"url": img} for img in product_data.get("images", [])[:16]]
        }
        
        response = self._make_request("POST", f"{self.BASE_URL}/sale/product-offers", headers=headers, json_data=listing_data)
        result = response.json()
        
        return {"marketplace_listing_id": result.get("id"), "url": f"https://allegro.pl/oferta/{result.get('id')}", "status": "active"}
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/vnd.allegro.public.v1+json"}
        listing_data = {"stock": {"available": product_data.get("quantity", 1)}, "sellingMode": {"price": {"amount": str(product_data.get("price")), "currency": "PLN"}}}
        response = self._make_request("PATCH", f"{self.BASE_URL}/sale/product-offers/{listing_id}", headers=headers, json_data=listing_data)
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self._make_request("DELETE", f"{self.BASE_URL}/sale/product-offers/{listing_id}", headers=headers)
        return response.status_code == 204
    
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self._make_request("GET", f"{self.BASE_URL}/sale/offers", headers=headers)
        return response.json().get("offers", [])
    
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self._make_request("GET", f"{self.BASE_URL}/sale/product-offers/{listing_id}", headers=headers)
        return response.json()
    
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        return {"message": "Allegro webhook implementation needed", "callback_url": callback_url}
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        return True

