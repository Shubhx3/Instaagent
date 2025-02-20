from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import requests
import json
import os
from datetime import datetime, timedelta

class InstagramAuthInput(BaseModel):
    """Input schema for Instagram Authentication Tool."""
    client_id: str = Field(..., description="Instagram App Client ID")
    client_secret: str = Field(..., description="Instagram App Client Secret")
    redirect_uri: str = Field(..., description="OAuth Redirect URI")
    code: Optional[str] = Field(None, description="Authorization code (if available)")

class InstagramAuthTool(BaseTool):
    name: str = "Instagram Authentication Tool"
    description: str = (
        "Manages Instagram API authentication using OAuth. Can initiate OAuth flow, "
        "exchange authorization codes for tokens, and refresh expired tokens."
    )
    args_schema: Type[BaseModel] = InstagramAuthInput
    
    def _run(self, input: InstagramAuthInput) -> str:
        """
        Handle Instagram authentication.
        
        If code is not provided, returns the authorization URL.
        If code is provided, exchanges it for access and refresh tokens.
        """
        # Store credentials securely (in a real implementation, use a secure storage method)
        self._save_credentials(input)
        
        if not input.code:
            # Generate authorization URL
            auth_url = (f"https://api.instagram.com/oauth/authorize"
                       f"?client_id={input.client_id}"
                       f"&redirect_uri={input.redirect_uri}"
                       f"&scope=user_profile,user_media"
                       f"&response_type=code")
            
            return f"Please authorize the application using this URL: {auth_url}"
        
        # Exchange code for tokens
        try:
            token_url = "https://api.instagram.com/oauth/access_token"
            payload = {
                "client_id": input.client_id,
                "client_secret": input.client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": input.redirect_uri,
                "code": input.code
            }
            
            response = requests.post(token_url, data=payload)
            response.raise_for_status()
            token_data = response.json()
            
            # Get long-lived token (for Instagram, short-lived tokens last 1 hour, long-lived last 60 days)
            long_lived_token = self._exchange_for_long_lived_token(
                client_secret=input.client_secret,
                access_token=token_data.get("access_token")
            )
            
            # Save tokens with expiry information
            tokens = {
                "access_token": long_lived_token.get("access_token"),
                "user_id": token_data.get("user_id"),
                "expires_at": (datetime.now() + timedelta(days=60)).timestamp()  # 60-day expiry
            }
            self._save_tokens(tokens)
            
            return f"Authentication successful. Access token valid until {datetime.fromtimestamp(tokens['expires_at']).strftime('%Y-%m-%d %H:%M:%S')}"
        
        except requests.exceptions.RequestException as e:
            return f"Authentication failed: {str(e)}"
    
    def _exchange_for_long_lived_token(self, client_secret: str, access_token: str) -> dict:
        """Exchange short-lived token for a long-lived token."""
        url = "https://graph.instagram.com/access_token"
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": client_secret,
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _save_credentials(self, input: InstagramAuthInput) -> None:
        """Save credentials to a secure location."""
        # In a production environment, use a secure storage method
        os.makedirs("credentials", exist_ok=True)
        with open("credentials/instagram_credentials.json", "w") as f:
            json.dump(input.dict(), f)
    
    def _save_tokens(self, tokens: dict) -> None:
        """Save tokens to a secure location."""
        # In a production environment, use a secure storage method
        os.makedirs("credentials", exist_ok=True)
        with open("credentials/instagram_tokens.json", "w") as f:
            json.dump(tokens, f)


class InstagramRefreshTokenInput(BaseModel):
    """Input schema for Instagram Token Refresh Tool."""
    pass  # No input needed as it uses stored tokens

class InstagramRefreshTokenTool(BaseTool):
    name: str = "Instagram Token Refresh Tool"
    description: str = (
        "Automatically refreshes Instagram access tokens before they expire."
    )
    args_schema: Type[BaseModel] = InstagramRefreshTokenInput
    
    def _run(self) -> str:
        """Refresh the Instagram access token if needed."""
        try:
            # Load current tokens
            with open("credentials/instagram_tokens.json", "r") as f:
                tokens = json.load(f)
            
            # Check if token needs refresh (refresh if less than 7 days remaining)
            expires_at = tokens.get("expires_at", 0)
            now = datetime.now().timestamp()
            
            # If token expires in less than 7 days, refresh it
            if expires_at - now < 7 * 24 * 60 * 60:
                # Load credentials
                with open("credentials/instagram_credentials.json", "r") as f:
                    credentials = json.load(f)
                
                # Refresh token
                url = "https://graph.instagram.com/refresh_access_token"
                params = {
                    "grant_type": "ig_refresh_token",
                    "access_token": tokens["access_token"]
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                refresh_data = response.json()
                
                # Update token data
                tokens["access_token"] = refresh_data["access_token"]
                tokens["expires_at"] = (datetime.now() + timedelta(days=60)).timestamp()
                
                # Save updated tokens
                with open("credentials/instagram_tokens.json", "w") as f:
                    json.dump(tokens, f)
                
                return f"Access token refreshed successfully. Valid until {datetime.fromtimestamp(tokens['expires_at']).strftime('%Y-%m-%d %H:%M:%S')}"
            
            return f"Token is still valid until {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}. No refresh needed."
        
        except FileNotFoundError:
            return "No token found. Please authenticate first."
        except requests.exceptions.RequestException as e:
            return f"Token refresh failed: {str(e)}"
