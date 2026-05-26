"""
GitHub App Authentication Service.
Generates installation access tokens so ReviewMind can act on behalf of
any user who installs the GitHub App on their repos.
"""
import time
import jwt
import requests
from app.core.config import settings


# Cache installation tokens (they last 1 hour)
_token_cache: dict[int, tuple[str, float]] = {}


def _generate_jwt() -> str:
    """Generate a JWT signed with the GitHub App's private key."""
    now = int(time.time())
    payload = {
        "iat": now - 60,          # Issued at (60s in past for clock drift)
        "exp": now + (10 * 60),   # Expires in 10 minutes
        "iss": settings.GITHUB_APP_ID,
    }
    return jwt.encode(payload, settings.GITHUB_APP_PRIVATE_KEY, algorithm="RS256")


def get_installation_token(installation_id: int) -> str:
    """
    Get an installation access token for a specific GitHub App installation.
    Tokens are cached for 50 minutes (they expire after 60).
    """
    # Check cache
    if installation_id in _token_cache:
        token, expires_at = _token_cache[installation_id]
        if time.time() < expires_at:
            return token

    # Generate new token
    app_jwt = _generate_jwt()
    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    token = data["token"]
    # Cache for 50 minutes (tokens last 60)
    _token_cache[installation_id] = (token, time.time() + 3000)

    return token


def is_github_app_configured() -> bool:
    """Check if GitHub App credentials are available."""
    return bool(settings.GITHUB_APP_ID and settings.GITHUB_APP_PRIVATE_KEY)
