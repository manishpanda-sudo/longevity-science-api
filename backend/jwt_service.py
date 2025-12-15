# jwt_service.py
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from auth_strategies import JWTStrategy, HS256Strategy, RS256Strategy
from config import SECRET_KEY, JWT_ALGORITHM, RSA_PRIVATE_KEY_PATH, RSA_PUBLIC_KEY_PATH, ACCESS_TOKEN_EXPIRE_MINUTES

logger = logging.getLogger(__name__)


class JWTService:
    """Context class that supports multiple JWT strategies"""
    
    def __init__(self, primary_strategy: JWTStrategy, fallback_strategies: Optional[List[JWTStrategy]] = None):
        self.primary_strategy = primary_strategy
        self.fallback_strategies = fallback_strategies or []
        logger.info(f"🎯 JWTService instance created with primary={primary_strategy.get_algorithm()}")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token using the PRIMARY strategy"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        token = self.primary_strategy.encode(to_encode)
        logger.info(f"🔑 Token created with {self.primary_strategy.get_algorithm()} for user={data.get('sub')}")
        return token
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token - tries PRIMARY then FALLBACK strategies"""
        logger.info(f"🔍 decode_token called with token: {token[:50]}...")
        logger.info(f"   Primary: {self.primary_strategy.get_algorithm()}")
        logger.info(f"   Fallbacks: {[s.get_algorithm() for s in self.fallback_strategies]}")
        
        # Try primary strategy first
        payload = self.primary_strategy.decode(token)
        if payload:
            logger.info(f"✅ Decoded with PRIMARY: {self.primary_strategy.get_algorithm()}")
            return payload
        else:
            logger.warning(f"❌ PRIMARY {self.primary_strategy.get_algorithm()} failed")
        
        # Try fallback strategies
        for i, strategy in enumerate(self.fallback_strategies):
            logger.info(f"🔄 Trying fallback {i+1}: {strategy.get_algorithm()}")
            payload = strategy.decode(token)
            if payload:
                logger.info(f"✅ Decoded with FALLBACK: {strategy.get_algorithm()}")
                return payload
            else:
                logger.warning(f"❌ FALLBACK {strategy.get_algorithm()} failed")
        
        logger.error("❌ ALL strategies failed!")
        return None
    
    def get_algorithm(self) -> str:
        """Get the current primary algorithm being used"""
        return self.primary_strategy.get_algorithm()


# Create a singleton instance at module load time
_jwt_service: Optional[JWTService] = None
_initialization_lock = False


def get_jwt_service() -> JWTService:
    """Get or create the JWT service with multi-strategy support"""
    global _jwt_service, _initialization_lock
    
    # Return existing instance if available
    if _jwt_service is not None:
        logger.debug(f"♻️ Returning existing JWT service (primary={_jwt_service.get_algorithm()})")
        return _jwt_service
    
    # Prevent multiple initializations
    if _initialization_lock:
        logger.warning("⚠️ JWT Service initialization already in progress!")
        import time
        time.sleep(0.1)  # Wait a bit
        if _jwt_service is not None:
            return _jwt_service
    
    _initialization_lock = True
    
    try:
        logger.info("=" * 60)
        logger.info("🚀 INITIALIZING JWT SERVICE (FIRST TIME)")
        logger.info(f"   JWT_ALGORITHM={JWT_ALGORITHM}")
        logger.info(f"   SECRET_KEY present={bool(SECRET_KEY)}, length={len(SECRET_KEY)}")
        logger.info("=" * 60)
        
        # Choose primary strategy based on config
        if JWT_ALGORITHM == "RS256":
            logger.info("📝 Attempting RS256 as primary")
            try:
                primary = RS256Strategy(
                    private_key_path=RSA_PRIVATE_KEY_PATH,
                    public_key_path=RSA_PUBLIC_KEY_PATH
                )
                logger.info("✅ RS256 primary initialized successfully")
                fallback = [HS256Strategy(SECRET_KEY)]
                logger.info("✅ HS256 fallback added")
            except Exception as e:
                logger.error(f"❌ RS256 failed: {e}, falling back to HS256")
                primary = HS256Strategy(SECRET_KEY)
                fallback = []
        else:  # HS256
            logger.info("📝 Using HS256 as primary")
            primary = HS256Strategy(SECRET_KEY)
            fallback = []
            try:
                fallback.append(RS256Strategy(
                    private_key_path=RSA_PRIVATE_KEY_PATH,
                    public_key_path=RSA_PUBLIC_KEY_PATH
                ))
                logger.info("✅ RS256 fallback added")
            except (FileNotFoundError, ValueError) as e:
                logger.info(f"⚠️ RS256 fallback not available: {e}")
        
        _jwt_service = JWTService(primary, fallback)
        logger.info(f"✅ JWT Service created successfully")
        logger.info(f"   Primary: {_jwt_service.get_algorithm()}")
        logger.info(f"   Fallbacks: {[s.get_algorithm() for s in _jwt_service.fallback_strategies]}")
        logger.info("=" * 60)
        
        return _jwt_service
    
    finally:
        _initialization_lock = False


# Initialize at module import time to ensure singleton
_jwt_service = None  # Will be initialized on first call