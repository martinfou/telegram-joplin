"""
OAuth2 Authentication Service for Google Tasks

Handles OAuth2 flow for Google Tasks API integration.
Provides authorization URLs and token management.
"""

import json
import os
import secrets
from typing import Any
from urllib.parse import urlencode

import requests


class GoogleAuthService:
    """Service for handling Google OAuth2 authentication"""

    AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPE = ["https://www.googleapis.com/auth/tasks"]

    def __init__(self, client_id: str = None, client_secret: str = None, redirect_uri: str = None):
        self.client_id = client_id or os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("GOOGLE_REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob")

        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth2 credentials not configured")

    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        """Generate OAuth2 authorization URL

        Returns:
            Tuple of (authorization_url, state)
        """
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.SCOPE),
            'response_type': 'code',
            'access_type': 'offline',
            'state': state
        }

        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_token(self, authorization_code: str) -> dict[str, Any]:
        """Exchange authorization code for access token

        Args:
            authorization_code: Code obtained from OAuth2 redirect

        Returns:
            Token dictionary with access_token, refresh_token, etc.
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()

        token = response.json()
        return token

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any] | None:
        """Refresh an expired access token

        Args:
            refresh_token: The refresh token

        Returns:
            New token dictionary or None if failed
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        try:
            response = requests.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def validate_token(self, access_token: str) -> bool:
        """Validate if access token is still valid"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo', headers=headers)

        return response.status_code == 200

    @staticmethod
    def save_token(user_id: str, token: dict[str, Any], token_file: str = "google_tokens.json"):
        """Save token for a user to file"""
        try:
            with open(token_file) as f:
                tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            tokens = {}

        tokens[user_id] = token

        with open(token_file, 'w') as f:
            json.dump(tokens, f, indent=2)

    @staticmethod
    def load_token(user_id: str, token_file: str = "google_tokens.json") -> dict[str, Any] | None:
        """Load token for a user from file"""
        try:
            with open(token_file) as f:
                tokens = json.load(f)
            return tokens.get(user_id)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    @staticmethod
    def delete_token(user_id: str, token_file: str = "google_tokens.json"):
        """Delete token for a user"""
        try:
            with open(token_file) as f:
                tokens = json.load(f)
            if user_id in tokens:
                del tokens[user_id]
                with open(token_file, 'w') as f:
                    json.dump(tokens, f, indent=2)
        except (FileNotFoundError, json.JSONDecodeError):
            pass


# Telegram bot integration for OAuth flow
class TelegramOAuthHandler:
    """Handle OAuth2 flow through Telegram bot interface"""

    def __init__(self, auth_service: GoogleAuthService):
        self.auth_service = auth_service
        self.pending_auths: dict[str, str] = {}  # state -> user_id

    def start_oauth_flow(self, user_id: str) -> str:
        """Start OAuth2 flow and return authorization URL"""
        auth_url, state = self.auth_service.get_authorization_url()
        self.pending_auths[state] = user_id
        return auth_url

    def complete_oauth_flow(self, authorization_code: str) -> dict[str, Any] | None:
        """Complete OAuth2 flow with authorization code"""
        try:
            token = self.auth_service.exchange_code_for_token(authorization_code)
            # In a real implementation, you'd need to know which user this is for
            # This would require storing state->user_id mapping
            return token
        except Exception as e:
            print(f"OAuth completion failed: {e}")
            return None


# Example usage
if __name__ == "__main__":
    try:
        auth_service = GoogleAuthService()
        print("✅ Google Auth service initialized")

        # Get authorization URL
        auth_url, state = auth_service.get_authorization_url()
        print(f"🔗 Authorization URL: {auth_url}")
        print(f"🔑 State: {state}")

        # Simulate token exchange (would get code from user)
        # code = input("Enter authorization code: ")
        # token = auth_service.exchange_code_for_token(code)
        # print(f"🎫 Token: {token}")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
