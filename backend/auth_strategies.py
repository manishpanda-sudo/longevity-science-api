# auth_strategies.py
from abc import ABC, abstractmethod
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os

class JWTStrategy(ABC):
    """Abstract base class for JWT signing strategies"""
    
    @abstractmethod
    def encode(self, payload: Dict[str, Any]) -> str:
        """Encode and sign a JWT token"""
        pass
    
    @abstractmethod
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token"""
        pass
    
    @abstractmethod
    def get_algorithm(self) -> str:
        """Return the algorithm name"""
        pass


class HS256Strategy(JWTStrategy):
    """HMAC SHA-256 symmetric signing strategy"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
    
    def encode(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None
    
    def get_algorithm(self) -> str:
        return self.algorithm


class RS256Strategy(JWTStrategy):
    """RSA SHA-256 asymmetric signing strategy"""
    
    def __init__(self, private_key_path: Optional[str] = None, public_key_path: Optional[str] = None):
        self.algorithm = "RS256"
        self.private_key = self._load_private_key(private_key_path) if private_key_path else None
        self.public_key = self._load_public_key(public_key_path) if public_key_path else None
    
    def _load_private_key(self, path: str):
        """Load RSA private key from file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Private key not found at {path}")
        
        with open(path, "rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
    
    def _load_public_key(self, path: str):
        """Load RSA public key from file"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Public key not found at {path}")
        
        with open(path, "rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
    
    def encode(self, payload: Dict[str, Any]) -> str:
        if not self.private_key:
            raise ValueError("Private key required for signing with RS256")
        
        # Convert private key to PEM format string for jose
        private_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return jwt.encode(payload, private_key_pem, algorithm=self.algorithm)
    
    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        if not self.public_key:
            raise ValueError("Public key required for verification with RS256")
        
        try:
            # Convert public key to PEM format string for jose
            public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return jwt.decode(token, public_key_pem, algorithms=[self.algorithm])
        except JWTError:
            return None
    
    def get_algorithm(self) -> str:
        return self.algorithm