# middleware/rate_limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


def get_user_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    Uses user ID if authenticated, otherwise IP address.
    """
    # Try to get user from token
    try:
        if hasattr(request.state, 'user'):
            user_id = request.state.user.id
            logger.debug(f"Rate limiting by user ID: {user_id}")
            return f"user:{user_id}"
    except:
        pass
    
    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        ip = request.client.host if request.client else "unknown"
    
    logger.debug(f"Rate limiting by IP: {ip}")
    return f"ip:{ip}"


# Initialize limiter
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Use in-memory storage (for production, use Redis)
    headers_enabled=True,
)


# Custom rate limit exceeded handler
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors
    """
    logger.warning(f"Rate limit exceeded for {get_user_identifier(request)}")
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after": getattr(exc, 'retry_after', None)
        },
        headers={
            "Retry-After": str(getattr(exc, 'retry_after', 60))
        }
    )