from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

from auth_strategies.strategies import JWTStrategy
from config import ACCESS_TOKEN_EXPIRE_MINUTES

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