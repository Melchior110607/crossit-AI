from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from time import sleep


class BaseMarketplaceConnector(ABC):
    """
    Abstract base class for all marketplace connectors
    Defines common interface and shared functionality
    """
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize connector with configuration
        
        Args:
            config: Dictionary containing API credentials and settings
        """
        self.config = config
        self.marketplace_name = self.__class__.__name__.replace("Connector", "").lower()
        self.rate_limit_delay = config.get("rate_limit_delay", 0.1)  # seconds between requests
    
    @abstractmethod
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """
        Initiate OAuth or API key authentication
        
        Returns:
            Dict containing authentication URL or tokens
        """
        pass
    
    @abstractmethod
    def exchange_code_for_token(self, code: str, **kwargs) -> Dict[str, str]:
        """
        Exchange OAuth authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Dict containing access_token, refresh_token, expires_at
        """
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh an expired access token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dict containing new access_token, refresh_token, expires_at
        """
        pass
    
    @abstractmethod
    def create_listing(self, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """
        Create a new product listing on the marketplace
        
        Args:
            product_data: Product information (title, description, price, images, etc.)
            access_token: User's access token for this marketplace
            
        Returns:
            Dict containing marketplace_listing_id, url, status
        """
        pass
    
    @abstractmethod
    def update_listing(self, listing_id: str, product_data: Dict, access_token: str) -> Dict[str, Any]:
        """
        Update an existing listing
        
        Args:
            listing_id: Marketplace's listing ID
            product_data: Updated product information
            access_token: User's access token
            
        Returns:
            Dict containing updated listing info
        """
        pass
    
    @abstractmethod
    def delete_listing(self, listing_id: str, access_token: str) -> bool:
        """
        Delete/delist a product listing
        
        Args:
            listing_id: Marketplace's listing ID
            access_token: User's access token
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def get_listings(self, access_token: str, **filters) -> List[Dict]:
        """
        Retrieve all listings for the user
        
        Args:
            access_token: User's access token
            filters: Optional filters (status, date_range, etc.)
            
        Returns:
            List of listing dictionaries
        """
        pass
    
    @abstractmethod
    def get_listing_details(self, listing_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific listing
        
        Args:
            listing_id: Marketplace's listing ID
            access_token: User's access token
            
        Returns:
            Dict with listing details
        """
        pass
    
    @abstractmethod
    def setup_webhook(self, callback_url: str, access_token: str) -> Dict[str, Any]:
        """
        Configure webhook for receiving marketplace notifications
        
        Args:
            callback_url: Our server's webhook endpoint
            access_token: User's access token
            
        Returns:
            Dict with webhook configuration info
        """
        pass
    
    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify that webhook request is authentic
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook headers
            secret: Webhook secret key
            
        Returns:
            True if signature is valid
        """
        pass
    
    # Helper methods (shared across all connectors)
    
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        max_retries: int = 3
    ) -> requests.Response:
        """
        Make HTTP request with retry logic and rate limiting
        """
        for attempt in range(max_retries):
            try:
                # Rate limiting
                sleep(self.rate_limit_delay)
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json_data,
                    params=params,
                    timeout=30
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Request failed after {max_retries} attempts: {str(e)}")
                sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Request failed")
    
    def _format_product_data(self, product_data: Dict) -> Dict:
        """
        Transform our internal product format to marketplace format
        Override this in subclasses for marketplace-specific formatting
        """
        return product_data
    
    def _parse_listing_response(self, response: Dict) -> Dict:
        """
        Parse marketplace response into our standard format
        Override this in subclasses
        """
        return response
    
    def _handle_api_error(self, error: Exception) -> Dict[str, str]:
        """
        Standardize error handling across all connectors
        """
        return {
            "error": True,
            "message": str(error),
            "marketplace": self.marketplace_name
        }

