from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from jose import jwt, JWTError, ExpiredSignatureError
import logging

logger = logging.getLogger(__name__)


class JWTStrategy(ABC):
    """Abstract base class for JWT encoding/decoding strategies"""
    
    @abstractmethod
    def encode(self, payload: dict) -> str:
        pass
    
    @abstractmethod
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_algorithm(self) -> str:
        pass


class HS256Strategy(JWTStrategy):
    """HMAC SHA-256 strategy using a secret key"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        logger.info(f"✨ HS256Strategy created (secret key length={len(secret_key)})")
    
    def encode(self, payload: dict) -> str:
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        logger.debug(f"HS256: Encoded payload={payload}")
        return token
    
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        logger.info(f"🔐 HS256: Attempting to decode token")
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            logger.info(f"✅ HS256: Successfully decoded! payload={payload}")
            return payload
        except ExpiredSignatureError:
            logger.warning("⏰ HS256: Token expired")
            return None
        except JWTError as e:
            logger.warning(f"❌ HS256: Invalid token - {type(e).__name__}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ HS256: Unexpected error - {type(e).__name__}: {str(e)}")
            return None
    
    def get_algorithm(self) -> str:
        return "HS256"


class RS256Strategy(JWTStrategy):
    """RSA SHA-256 strategy using public/private key pair"""
    
    def __init__(self, private_key_path: str, public_key_path: str):
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        logger.info(f"✨ RS256Strategy initializing...")
        self._load_keys()
    
    def _load_keys(self):
        """Load RSA keys from files"""
        import os
        
        # Load private key
        if os.path.exists(self.private_key_path):
            with open(self.private_key_path, 'r') as f:
                self.private_key = f.read()
            logger.info(f"✅ RS256: Private key loaded ({len(self.private_key)} bytes)")
        else:
            logger.warning(f"⚠️ RS256: Private key not found at {self.private_key_path}")
            self.private_key = None
        
        # Load public key
        if os.path.exists(self.public_key_path):
            with open(self.public_key_path, 'r') as f:
                self.public_key = f.read()
            logger.info(f"✅ RS256: Public key loaded ({len(self.public_key)} bytes)")
        else:
            logger.error(f"❌ RS256: Public key not found at {self.public_key_path}")
            raise ValueError(f"Public key not found at {self.public_key_path}")
    
    def encode(self, payload: dict) -> str:
        if not self.private_key:
            raise ValueError("Private key not available")
        token = jwt.encode(payload, self.private_key, algorithm="RS256")
        logger.debug(f"RS256: Encoded payload={payload}")
        return token
    
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        logger.info(f"🔐 RS256: Attempting to decode token")
        try:
            payload = jwt.decode(token, self.public_key, algorithms=["RS256"])
            logger.info(f"✅ RS256: Successfully decoded! payload={payload}")
            return payload
        except ExpiredSignatureError:
            logger.warning("⏰ RS256: Token expired")
            return None
        except JWTError as e:
            logger.warning(f"❌ RS256: Invalid token - {type(e).__name__}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ RS256: Unexpected error - {type(e).__name__}: {str(e)}")
            return None
    
    def get_algorithm(self) -> str:
        return "RS256"