from typing import Dict, List, Any
from app.integrations.base_connector import BaseMarketplaceConnector


class BolConnector(BaseMarketplaceConnector):
    """bol.com Retailer API connector - https://api.bol.com"""
    
    BASE_URL = "https://api.bol.com"
    AUTH_URL = "https://login.bol.com/authorize"
    TOKEN_URL = "https://login.bol.com/token"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        
        return {
            "auth_url": f"{self.AUTH_URL}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code",
            "marketplace": "bol"
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret")
        }
        response = self._make_request("POST", self.TOKEN_URL, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": token_data.get("expires_in")
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret")
        }
        response = self._make_request("POST", self.TOKEN_URL, data=data)
        token_data = response.json()
        return {"access_token": token_data.get("access_token"), "refresh_token": refresh_token, "expires_at": token_data.get("expires_in")}
    
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/vnd.retailer.v10+json"}
        
        listing_data = {
            "ean": product_data.get("ean", "0000000000000"),
            "condition": {"name": product_data.get("condition", "NEW")},
            "referenceCode": product_data.get("sku"),
            "onHoldByRetailer": False,
            "stock": {"amount": product_data.get("quantity", 1)},
            "pricing": {"bundlePrices": [{"quantity": 1, "unitPrice": product_data.get("price")}]}
        }
        
        response = self._make_request("POST", f"{self.BASE_URL}/retailer/offers", headers=headers, json_data=listing_data)
        result = response.json()
        
        return {"marketplace_listing_id": result.get("offerId"), "url": f"https://www.bol.com/nl/p/{result.get('offerId')}", "status": "active"}
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/vnd.retailer.v10+json"}
        listing_data = {"stock": {"amount": product_data.get("quantity", 1)}, "pricing": {"bundlePrices": [{"quantity": 1, "unitPrice": product_data.get("price")}]}}
        response = self._make_request("PUT", f"{self.BASE_URL}/retailer/offers/{listing_id}", headers=headers, json_data=listing_data)
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self._make_request("DELETE", f"{self.BASE_URL}/retailer/offers/{listing_id}", headers=headers)
        return response.status_code == 202
    
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self._make_request("GET", f"{self.BASE_URL}/retailer/offers", headers=headers)
        return response.json().get("offers", [])
    
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self._make_request("GET", f"{self.BASE_URL}/retailer/offers/{listing_id}", headers=headers)
        return response.json()
    
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/vnd.retailer.v10+json"}
        data = {"url": callback_url, "subscriptionType": "OFFER"}
        response = self._make_request("POST", f"{self.BASE_URL}/retailer/subscriptions", headers=headers, json_data=data)
        return response.json()
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        return True  # Implement proper verification

