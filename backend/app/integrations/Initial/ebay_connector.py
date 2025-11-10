from typing import Dict, List, Optional, Any
from app.integrations.base_connector import BaseMarketplaceConnector
import base64


class EbayConnector(BaseMarketplaceConnector):
    """
    eBay API connector (Trading & Inventory APIs)
    Documentation: https://developer.ebay.com/
    """
    
    BASE_URL = "https://api.ebay.com"
    AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
    TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
    
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Initiate eBay OAuth flow"""
        client_id = self.config.get("client_id")
        redirect_uri = self.config.get("redirect_uri")
        scopes = "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.inventory"
        
        auth_url = (
            f"{self.AUTH_URL}"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope={scopes}"
        )
        
        return {
            "auth_url": auth_url,
            "marketplace": "ebay"
        }
    
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        """Exchange authorization code for access token"""
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
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": token_data.get("expires_in"),
            "token_type": token_data.get("token_type")
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh eBay access token"""
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
            "refresh_token": refresh_token,
            "scope": "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.inventory"
        }
        
        response = self._make_request("POST", self.TOKEN_URL, headers=headers, data=data)
        token_data = response.json()
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": refresh_token,  # eBay doesn't return new refresh token
            "expires_at": token_data.get("expires_in")
        }
    
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """Create eBay listing using Inventory API"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Content-Language": "en-US"
        }
        
        # Step 1: Create inventory item
        sku = product_data.get("sku", f"item-{product_data.get('id')}")
        inventory_url = f"{self.BASE_URL}/sell/inventory/v1/inventory_item/{sku}"
        
        inventory_data = self._format_ebay_inventory(product_data)
        self._make_request("PUT", inventory_url, headers=headers, json_data=inventory_data)
        
        # Step 2: Create offer
        offer_url = f"{self.BASE_URL}/sell/inventory/v1/offer"
        offer_data = self._format_ebay_offer(product_data, sku)
        
        response = self._make_request("POST", offer_url, headers=headers, json_data=offer_data)
        offer = response.json()
        
        # Step 3: Publish offer
        offer_id = offer.get("offerId")
        publish_url = f"{self.BASE_URL}/sell/inventory/v1/offer/{offer_id}/publish"
        publish_response = self._make_request("POST", publish_url, headers=headers)
        
        listing_id = publish_response.json().get("listingId")
        
        return {
            "marketplace_listing_id": listing_id,
            "url": f"https://www.ebay.com/itm/{listing_id}",
            "status": "active"
        }
    
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """Update eBay listing"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        sku = product_data.get("sku", listing_id)
        url = f"{self.BASE_URL}/sell/inventory/v1/inventory_item/{sku}"
        
        inventory_data = self._format_ebay_inventory(product_data)
        response = self._make_request("PUT", url, headers=headers, json_data=inventory_data)
        
        return response.json()
    
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        """End/delete eBay listing"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}/sell/inventory/v1/offer/{listing_id}/withdraw"
        
        response = self._make_request("POST", url, headers=headers)
        return response.status_code == 200
    
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        """Get eBay inventory items"""
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        url = f"{self.BASE_URL}/sell/inventory/v1/inventory_item"
        
        response = self._make_request("GET", url, headers=headers, params=filters)
        return response.json().get("inventoryItems", [])
    
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        """Get eBay listing details"""
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        url = f"{self.BASE_URL}/sell/inventory/v1/inventory_item/{listing_id}"
        
        response = self._make_request("GET", url, headers=headers)
        return response.json()
    
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        """Setup eBay notification subscription"""
        # eBay uses notification API
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        subscription_data = {
            "topic": "MARKETPLACE_ACCOUNT_DELETION",
            "deliveryConfig": {
                "endpoint": callback_url,
                "verificationToken": self.config.get("verification_token")
            }
        }
        
        url = f"{self.BASE_URL}/commerce/notification/v1/subscription"
        
        response = self._make_request("POST", url, headers=headers, json_data=subscription_data)
        return response.json()
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify eBay webhook signature"""
        # eBay uses verification token in headers
        return True  # Implement proper verification
    
    def _format_ebay_inventory(self, product_data: Dict) -> Dict:
        """Format product data for eBay inventory item"""
        return {
            "availability": {
                "shipToLocationAvailability": {
                    "quantity": product_data.get("quantity", 1)
                }
            },
            "condition": product_data.get("condition", "NEW").upper(),
            "product": {
                "title": product_data.get("title"),
                "description": product_data.get("description"),
                "imageUrls": product_data.get("images", []),
                "aspects": {
                    "Brand": [product_data.get("brand", "Unbranded")],
                    "Type": [product_data.get("category", "Other")]
                }
            }
        }
    
    def _format_ebay_offer(self, product_data: Dict, sku: str) -> Dict:
        """Format offer data for eBay"""
        return {
            "sku": sku,
            "marketplaceId": "EBAY_US",
            "format": "FIXED_PRICE",
            "availableQuantity": product_data.get("quantity", 1),
            "categoryId": "111",  # Default category - should be mapped properly
            "listingDescription": product_data.get("description"),
            "pricingSummary": {
                "price": {
                    "value": str(product_data.get("price")),
                    "currency": "USD"
                }
            },
            "listingPolicies": {
                "fulfillmentPolicyId": self.config.get("fulfillment_policy_id"),
                "paymentPolicyId": self.config.get("payment_policy_id"),
                "returnPolicyId": self.config.get("return_policy_id")
            }
        }

