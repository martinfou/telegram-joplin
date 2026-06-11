"""
Google Tasks Integration for Telegram-Joplin Bot

This module provides integration with Google Tasks API to automatically
create tasks from AI-identified action items in notes.

Setup Requirements:
1. Google Cloud Console project
2. Google Tasks API enabled
3. OAuth2 credentials (client ID and secret)
4. Authorized redirect URIs for OAuth flow

Environment Variables:
- GOOGLE_CLIENT_ID: OAuth2 client ID
- GOOGLE_CLIENT_SECRET: OAuth2 client secret
- GOOGLE_REDIRECT_URI: OAuth redirect URI (for web-based auth)

Usage:
    client = GoogleTasksClient()
    task = client.create_task("Buy groceries", "Milk, bread, eggs")
"""

import logging
import os
from collections.abc import Callable
from typing import Any

from requests_oauthlib import OAuth2Session

from src.exceptions import GoogleAuthError

logger = logging.getLogger(__name__)


class GoogleTasksClient:
    """Client for Google Tasks API integration"""

    BASE_URL = "https://www.googleapis.com/tasks/v1"
    AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPE = ["https://www.googleapis.com/auth/tasks"]

    @property
    def scope(self):
        return self.SCOPE

    def __init__(self, client_id: str | None = None, client_secret: str | None = None, redirect_uri: str | None = None):
        self.client_id = client_id or os.getenv("GOOGLE_CLIENT_ID") or ""
        self.client_secret = client_secret or os.getenv("GOOGLE_CLIENT_SECRET") or ""
        self.redirect_uri = redirect_uri or os.getenv("GOOGLE_REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob")

        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth2 credentials not configured")

        self.session: OAuth2Session | None = None
        self.token: dict[str, Any] | None = None

    def get_authorization_url(self) -> tuple[str, str]:
        """Get OAuth2 authorization URL and state"""
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        )

        authorization_url, state = session.authorization_url(
            self.AUTH_URL,
            access_type="offline",
        )

        return authorization_url, state

    def exchange_code_for_token(self, authorization_code: str) -> dict[str, Any]:
        """Exchange authorization code for access token"""
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri
        )

        token = session.fetch_token(
            token_url=self.TOKEN_URL,
            client_secret=self.client_secret,
            code=authorization_code
        )

        self.token = token
        self.session = OAuth2Session(
            client_id=self.client_id,
            token=token
        )

        return token

    def set_token(
        self,
        token: dict[str, Any],
        *,
        token_updater: Callable[[dict[str, Any]], None] | None = None,
    ):
        """Set access token for authenticated requests.
        If token_updater is provided, enables auto-refresh so expired tokens
        are refreshed automatically and the callback is invoked with the new token."""
        self.token = token.copy()
        # Ensure expires_in exists for auto-refresh (Google returns it; default 1h if missing)
        if "expires_in" not in self.token and "expires_at" not in self.token:
            self.token["expires_in"] = 3600
        if token_updater:

            def _updater(new_token: dict[str, Any]) -> None:
                if new_token and self.token and self.token.get("refresh_token") and not new_token.get("refresh_token"):
                    new_token = {**new_token, "refresh_token": self.token["refresh_token"]}
                self.token = new_token
                token_updater(new_token)

            self.session = OAuth2Session(
                client_id=self.client_id,
                token=self.token,
                auto_refresh_url=self.TOKEN_URL,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                token_updater=_updater,
            )
        else:
            self.session = OAuth2Session(
                client_id=self.client_id,
                token=self.token,
            )

    def refresh_token(self) -> dict[str, Any] | None:
        """Refresh expired access token. Preserves refresh_token from the previous token
        since Google's refresh response often only returns access_token and expires_in."""
        if not self.session or not self.token:
            return None

        try:
            new_token = self.session.refresh_token(
                token_url=self.TOKEN_URL,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            # Merge so we never lose refresh_token (Google does not return it on refresh)
            if new_token and self.token.get("refresh_token") and not new_token.get("refresh_token"):
                new_token = {**new_token, "refresh_token": self.token["refresh_token"]}
            self.token = new_token
            return self.token
        except Exception as e:
            logger.debug(f"Token refresh failed: {e}")
            return None

    def get_task_lists(self) -> list[dict[str, Any]]:
        """Get all user's task lists"""
        if not self.session:
            raise ValueError("Not authenticated")

        try:
            response = self.session.get(f"{self.BASE_URL}/users/@me/lists")
            response.raise_for_status()
            return response.json().get("items", [])
        except Exception as e:
            error_str = str(e).lower()
            # Handle token expiration (can be ValueError, HTTPError, or other)
            if "token_expired" in error_str or "401" in error_str:
                logger.debug("Token expired, attempting refresh...")
                if self.refresh_token():
                    # Retry after refresh
                    try:
                        response = self.session.get(f"{self.BASE_URL}/users/@me/lists")
                        response.raise_for_status()
                        return response.json().get("items", [])
                    except Exception as retry_error:
                        logger.debug(f"Failed to get task lists after refresh: {retry_error}")
                        return []
                else:
                    logger.debug("Token refresh failed")
                    return []
            else:
                logger.debug(f"Failed to get task lists: {e}")
                return []

    def get_default_task_list(self) -> str:
        """Get the default task list ID"""
        task_lists = self.get_task_lists()
        if task_lists:
            return task_lists[0]["id"]
        raise ValueError("No task lists found")

    def create_task(
        self,
        title: str,
        notes: str = "",
        task_list_id: str | None = None,
        due_date: str | None = None,
        parent_task_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Create a new task in Google Tasks. FR-034: parent_task_id creates a subtask."""
        if not self.session:
            raise ValueError("Not authenticated")

        if not task_list_id:
            task_list_id = self.get_default_task_list()
            if not task_list_id:
                raise ValueError("No default task list found")

        task_data = {
            "title": title,
            "notes": notes
        }

        if due_date:
            # Google Tasks expects RFC3339 format
            task_data["due"] = due_date

        try:
            url = f"{self.BASE_URL}/lists/{task_list_id}/tasks"
            if parent_task_id:
                url += f"?parent={parent_task_id}"
            response = self.session.post(url, json=task_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_str = str(e).lower()
            # Handle token expiration
            if "token_expired" in error_str or "401" in error_str:
                logger.debug("Token expired, attempting refresh...")
                if self.refresh_token():
                    # Retry after refresh
                    try:
                        response = self.session.post(url, json=task_data)
                        response.raise_for_status()
                        return response.json()
                    except Exception as retry_error:
                        logger.debug("Failed to create task after refresh: %s", retry_error)
                        raise retry_error
                else:
                    logger.debug("Token refresh failed")
                    raise GoogleAuthError("Token expired and refresh failed") from e
            else:
                logger.debug("Failed to create task: %s", e)
                raise

    def update_task(self, task_id: str, task_list_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update an existing task"""
        if not self.session:
            raise ValueError("Not authenticated")

        try:
            url = f"{self.BASE_URL}/lists/{task_list_id}/tasks/{task_id}"
            response = self.session.patch(url, json=updates)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            error_str = str(e).lower()
            # Handle token expiration
            if "token_expired" in error_str or "401" in error_str:
                logger.debug("Token expired, attempting refresh...")
                if self.refresh_token():
                    # Retry after refresh
                    try:
                        response = self.session.patch(url, json=updates)
                        response.raise_for_status()
                        return response.json()
                    except Exception as retry_error:
                        logger.debug(f"Failed to update task after refresh: {retry_error}")
                        return None
                else:
                    logger.debug("Token refresh failed")
                    return None
            else:
                logger.debug(f"Failed to update task: {e}")
                return None

    def delete_task(self, task_id: str, task_list_id: str) -> bool:
        """Delete a task"""
        if not self.session:
            raise ValueError("Not authenticated")

        try:
            url = f"{self.BASE_URL}/lists/{task_list_id}/tasks/{task_id}"
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except Exception as e:
            error_str = str(e).lower()
            # Handle token expiration
            if "token_expired" in error_str or "401" in error_str:
                logger.debug("Token expired, attempting refresh...")
                if self.refresh_token():
                    # Retry after refresh
                    try:
                        url = f"{self.BASE_URL}/lists/{task_list_id}/tasks/{task_id}"
                        response = self.session.delete(url)
                        response.raise_for_status()
                        return True
                    except Exception as retry_error:
                        logger.debug(f"Failed to delete task after refresh: {retry_error}")
                        return False
                else:
                    logger.debug("Token refresh failed")
                    return False
            else:
                logger.debug(f"Failed to delete task: {e}")
                return False

    def get_tasks(self, task_list_id: str, show_completed: bool = False, max_results: int = 100) -> list[dict[str, Any]]:
        """Get tasks from a task list"""
        if not self.session:
            raise ValueError("Not authenticated")

        params = {
            "maxResults": max_results,
            "showCompleted": show_completed
        }

        try:
            url = f"{self.BASE_URL}/lists/{task_list_id}/tasks"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except Exception as e:
            error_str = str(e).lower()
            # Handle token expiration
            if "token_expired" in error_str or "401" in error_str:
                logger.debug("Token expired, attempting refresh...")
                if self.refresh_token():
                    # Retry after refresh
                    try:
                        response = self.session.get(url, params=params)
                        response.raise_for_status()
                        return response.json().get("items", [])
                    except Exception as retry_error:
                        logger.debug(f"Failed to get tasks after refresh: {retry_error}")
                        return []
                else:
                    logger.debug("Token refresh failed")
                    return []
            else:
                logger.debug(f"Failed to get tasks: {e}")
                return []

    def get_all_tasks(
        self, task_list_id: str, show_completed: bool = False
    ) -> list[dict[str, Any]]:
        """Get all tasks from a task list, handling pagination."""
        all_tasks: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            params: dict[str, Any] = {
                "maxResults": 100,
                "showCompleted": show_completed,
            }
            if page_token:
                params["pageToken"] = page_token
            if not self.session:
                raise ValueError("Not authenticated")
            try:
                url = f"{self.BASE_URL}/lists/{task_list_id}/tasks"
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])
                all_tasks.extend(items)
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
            except Exception as e:
                logger.debug("Failed to fetch tasks page: %s", e)
                break
        return all_tasks


# Example usage and testing
if __name__ == "__main__":
    # Test the client setup
    try:
        client = GoogleTasksClient()
        print("✅ Google Tasks client initialized")
        print(f"Client ID configured: {bool(client.client_id)}")
        print(f"Client Secret configured: {bool(client.client_secret)}")

        # Get authorization URL (would be used in web interface)
        auth_url, state = client.get_authorization_url()
        print(f"Authorization URL: {auth_url}")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
