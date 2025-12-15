# jwt_service.py
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from auth_strategies import JWTStrategy, HS256Strategy, RS256Strategy
from config import SECRET_KEY, JWT_ALGORITHM, RSA_PRIVATE_KEY_PATH, RSA_PUBLIC_KEY_PATH, ACCESS_TOKEN_EXPIRE_MINUTES


class JWTService:
    """Context class that supports multiple JWT strategies"""
    
    def __init__(self, primary_strategy: JWTStrategy, fallback_strategies: Optional[List[JWTStrategy]] = None):
        self.primary_strategy = primary_strategy  # Used for signing NEW tokens
        self.fallback_strategies = fallback_strategies or []  # Used for verifying OLD tokens
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token using the PRIMARY strategy"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        return self.primary_strategy.encode(to_encode)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token - tries PRIMARY then FALLBACK strategies"""
        # Try primary strategy first
        payload = self.primary_strategy.decode(token)
        if payload:
            return payload
        
        # Try fallback strategies
        for strategy in self.fallback_strategies:
            payload = strategy.decode(token)
            if payload:
                return payload
        
        return None
    
    def get_algorithm(self) -> str:
        """Get the current primary algorithm being used"""
        return self.primary_strategy.get_algorithm()


# Create a singleton instance
_jwt_service = None

def get_jwt_service() -> JWTService:
    """Get or create the JWT service with multi-strategy support"""
    global _jwt_service
    if _jwt_service is None:
        # Choose primary strategy based on config
        if JWT_ALGORITHM == "RS256":
            primary = RS256Strategy(
                private_key_path=RSA_PRIVATE_KEY_PATH,
                public_key_path=RSA_PUBLIC_KEY_PATH
            )
            # Keep HS256 as fallback to verify old tokens
            fallback = [HS256Strategy(SECRET_KEY)]
        else:  # HS256
            primary = HS256Strategy(SECRET_KEY)
            # Optionally add RS256 as fallback if keys exist
            fallback = []
            try:
                fallback.append(RS256Strategy(
                    private_key_path=RSA_PRIVATE_KEY_PATH,
                    public_key_path=RSA_PUBLIC_KEY_PATH
                ))
            except (FileNotFoundError, ValueError):
                pass  # RS256 keys not available
        
        _jwt_service = JWTService(primary, fallback)
    return _jwt_service