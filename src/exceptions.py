"""
Domain exceptions for clean error handling.

Each subsystem raises its own exception type so callers can handle
failures precisely instead of catching bare Exception.
"""


class AppError(Exception):
    """Base for all application errors."""

    def __init__(self, message: str = "", *, user_message: str | None = None):
        super().__init__(message)
        self.user_message = user_message or "Something went wrong. Please try again."


# --- Joplin ---

class JoplinError(AppError):
    """Raised when a Joplin API call fails."""

    def __init__(self, message: str = "Joplin API error", *, status_code: int | None = None):
        super().__init__(
            message,
            user_message="I can't reach Joplin right now. Please make sure it's running.",
        )
        self.status_code = status_code


class JoplinConnectionError(JoplinError):
    """Joplin is unreachable (network / not running)."""


class JoplinAuthError(JoplinError):
    """Joplin returned 403 — bad or missing token."""

    def __init__(self):
        super().__init__("Joplin authentication failed (403)", status_code=403)
        self.user_message = "Joplin rejected the API token. Check JOPLIN_WEB_CLIPPER_TOKEN."


# --- LLM ---

class LLMError(AppError):
    """Raised when an LLM provider call fails."""

    def __init__(self, message: str = "LLM provider error"):
        super().__init__(
            message,
            user_message="The AI service isn't responding. Please try again in a moment.",
        )


class LLMProviderUnavailable(LLMError):
    """No configured LLM provider is available."""


class LLMParseError(LLMError):
    """LLM returned a response that couldn't be parsed into the expected schema."""


# --- Google Tasks ---

class GoogleTasksError(AppError):
    """Raised when a Google Tasks API call fails."""

    def __init__(self, message: str = "Google Tasks error"):
        super().__init__(
            message,
            user_message="There was a problem with Google Tasks. Please try again.",
        )


class GoogleAuthError(GoogleTasksError):
    """Google OAuth flow or token refresh failed."""

    def __init__(self, message: str = "Google authentication failed"):
        super().__init__(message)
        self.user_message = (
            "Your Google token expired and could not be refreshed. "
            "Use /tasks_connect to re-connect."
        )


class GoogleTasksConfigError(GoogleTasksError):
    """Google Tasks not configured or disabled for user."""

    def __init__(self, message: str, user_message: str | None = None):
        super().__init__(message)
        self.user_message = user_message or "Google Tasks is not set up. Use /tasks_connect first."
