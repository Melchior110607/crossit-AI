"""
Generic OAuth Service for all marketplaces (SUPABASE VERSION)
Handles OAuth 2.0 flows, token storage, and refresh
"""
import requests
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import urllib.parse
import secrets
from app.core.supabase import supabase_admin

class OAuthService:
    """Base OAuth Service class using Supabase"""
    
    def __init__(
        self,
        marketplace_id: str,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        redirect_uri: str,
        scopes: list[str] = None,
        extra_params: Dict[str, str] = None
    ):
        self.marketplace_id = marketplace_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.scopes = scopes or []
        self.extra_params = extra_params or {}
    
    def generate_authorization_url(self, user_id: str, state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate OAuth authorization URL
        Returns: { "url": "https://...", "state": "random_state" }
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
        }
        
        if self.scopes:
            params["scope"] = " ".join(self.scopes)
        
        # Add marketplace-specific extra parameters (e.g., eBay ru_name)
        if self.extra_params:
            params.update(self.extra_params)
        
        # Store state in DB for verification (future: use Redis)
        self._store_oauth_state(user_id, state)
        
        # Use quote_via=urllib.parse.quote to ensure spaces are encoded as %20, not +
        url = f"{self.authorization_url}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
        return {"url": url, "state": state}
    
    def exchange_code_for_token(self, code: str, user_id: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        Returns: { "access_token": "...", "refresh_token": "...", "expires_at": timestamp }
        """
        # eBay requires Basic Auth (credentials in Authorization header, not in body)
        if self.marketplace_id == "ebay":
            import base64
            
            # Create Basic Auth credentials (client_id:client_secret encoded in base64)
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}"
            }
            
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
            
            response = requests.post(self.token_url, data=data, headers=headers)
        else:
            # Standard OAuth flow (credentials in body)
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            response = requests.post(self.token_url, data=data)
        
        response.raise_for_status()
        
        token_data = response.json()
        
        # Calculate expiration timestamp
        expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        # Store tokens in Supabase
        self._store_tokens(
            user_id=user_id,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
            expires_at=int(expires_at.timestamp())  # Unix timestamp for return value
        )
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "expires_at": int(expires_at.timestamp()),
            "token_type": token_data.get("token_type", "Bearer")
        }
    
    def refresh_access_token(self, refresh_token: str, user_id: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        """
        # eBay requires Basic Auth (credentials in Authorization header, not in body)
        if self.marketplace_id == "ebay":
            import base64
            
            # Create Basic Auth credentials (client_id:client_secret encoded in base64)
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
            
            response = requests.post(self.token_url, data=data, headers=headers)
        else:
            # Standard OAuth flow (credentials in body)
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            
            response = requests.post(self.token_url, data=data)
        
        response.raise_for_status()
        
        token_data = response.json()
        
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        # Update tokens in Supabase
        self._store_tokens(
            user_id=user_id,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token", refresh_token),
            expires_at=int(expires_at.timestamp())
        )
        
        return {
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token", refresh_token),
            "expires_at": int(expires_at.timestamp())
        }
    
    def get_valid_token(self, user_id: str) -> Optional[str]:
        """
        Get a valid access token (refresh if expired)
        """
        response = supabase_admin.table("marketplace_connections").select("*").eq(
            "user_id", user_id
        ).eq("marketplace_id", self.marketplace_id).eq("status", "active").execute()
        
        if not response.data:
            return None
        
        connection = response.data[0]
        access_token = connection.get("access_token")
        refresh_token = connection.get("refresh_token")
        expires_at_unix = connection.get("token_expires_at")  # Unix timestamp (integer)
        
        if expires_at_unix:
            # Convert Unix timestamp to datetime
            expires_at = datetime.fromtimestamp(expires_at_unix)
            # Check if token is expired (with 5 min buffer)
            if expires_at < datetime.now() + timedelta(minutes=5):
                if refresh_token:
                    # Refresh the token
                    new_tokens = self.refresh_access_token(refresh_token, user_id)
                    return new_tokens["access_token"]
                return None
        
        return access_token
    
    def disconnect(self, user_id: str) -> bool:
        """
        Disconnect marketplace (soft delete - update status)
        """
        response = supabase_admin.table("marketplace_connections").update({
            "status": "disconnected",
            "updated_at": int(datetime.now().timestamp())
        }).eq("user_id", user_id).eq("marketplace_id", self.marketplace_id).execute()
        
        return len(response.data) > 0
    
    # Private helper methods
    
    def _store_oauth_state(self, user_id: str, state: str):
        """Store OAuth state for CSRF protection"""
        # TODO: Store in Redis or temporary cache
        # For now, simplified version
        pass
    
    def _store_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: Optional[str],
        expires_at: int  # Unix timestamp (integer)
    ):
        """Store or update tokens in Supabase"""
        # Check if connection exists
        existing = supabase_admin.table("marketplace_connections").select("id").eq(
            "user_id", user_id
        ).eq("marketplace_id", self.marketplace_id).execute()
        
        # Convert Unix timestamps to datetime objects for PostgreSQL
        now = datetime.now()
        expires_at_dt = datetime.fromtimestamp(expires_at)
        
        data = {
            "user_id": user_id,
            "marketplace_id": self.marketplace_id,
            "marketplace_name": self.marketplace_id.title(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expires_at": int(expires_at),  # Keep as INTEGER for schema.sql compatibility
            "auth_type": "oauth2",
            "status": "active",
            "updated_at": int(now.timestamp())
        }
        
        if existing.data:
            # Update existing connection
            supabase_admin.table("marketplace_connections").update(data).eq(
                "user_id", user_id
            ).eq("marketplace_id", self.marketplace_id).execute()
        else:
            # Create new connection
            data["created_at"] = int(now.timestamp())
            data["id"] = f"{user_id}_{self.marketplace_id}"  # Generate unique ID
            supabase_admin.table("marketplace_connections").insert(data).execute()


class APIKeyService:
    """Service for marketplaces using API Keys (not OAuth) - SUPABASE VERSION"""
    
    def __init__(self, marketplace_id: str):
        self.marketplace_id = marketplace_id
    
    def store_api_key(
        self,
        user_id: str,
        api_key: str,
        api_secret: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store API key in Supabase"""
        now_timestamp = int(datetime.now().timestamp())
        
        data = {
            "user_id": user_id,
            "marketplace_id": self.marketplace_id,
            "marketplace_name": self.marketplace_id.title(),
            "auth_type": "api_key",
            "api_key": api_key,
            "api_secret": api_secret,
            "status": "active",
            "created_at": now_timestamp,
            "updated_at": now_timestamp
        }
        
        # Upsert (insert or update)
        response = supabase_admin.table("marketplace_connections").upsert(data).execute()
        return len(response.data) > 0
    
    def get_api_key(self, user_id: str) -> Optional[Dict[str, str]]:
        """Get API key from Supabase"""
        response = supabase_admin.table("marketplace_connections").select(
            "api_key,api_secret"
        ).eq("user_id", user_id).eq("marketplace_id", self.marketplace_id).eq(
            "status", "active"
        ).execute()
        
        if response.data:
            row = response.data[0]
            return {"api_key": row.get("api_key"), "api_secret": row.get("api_secret")}
        return None
