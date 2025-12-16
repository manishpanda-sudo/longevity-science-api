from typing import Optional
import logging
import time

from auth_strategies.service import JWTService
from auth_strategies.strategies import HS256Strategy, RS256Strategy
from config import SECRET_KEY, JWT_ALGORITHM, RSA_PRIVATE_KEY_PATH, RSA_PUBLIC_KEY_PATH

logger = logging.getLogger(__name__)

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