from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def calculate_health_analysis(biomarkers: pd.Series, chronological_age: int) -> Dict[str, Any]:
    """Calculate health scores and biological age from biomarkers"""
    
    age_modifier = 0
    
    # 1. Cholesterol/HDL Ratio
    chol_hdl_ratio = biomarkers['cholesterol_total'] / biomarkers['hdl']
    if chol_hdl_ratio < 3.5:
        age_modifier -= 3
        cv_risk = "low"
    elif chol_hdl_ratio < 5.0:
        age_modifier += 0
        cv_risk = "medium"
    else:
        age_modifier += 4
        cv_risk = "high"
    
    # 2. CRP (Inflammation)
    crp = biomarkers['crp']
    if crp < 1.0:
        inflammation_score = 90
        age_modifier -= 2
    elif crp < 3.0:
        inflammation_score = 70
        age_modifier += 1
    else:
        inflammation_score = 40
        age_modifier += 3
    
    # 3. Glucose
    glucose = biomarkers['glucose']
    if glucose < 100:
        metabolic_score = 95
        age_modifier -= 2
    elif glucose < 126:
        metabolic_score = 65
        age_modifier += 2
    else:
        metabolic_score = 35
        age_modifier += 5
    
    # 4. Triglycerides
    triglycerides = biomarkers['triglycerides']
    if triglycerides < 100:
        age_modifier -= 1
    elif triglycerides > 200:
        age_modifier += 2
    
    # 5. Vitamin D
    vitamin_d = biomarkers['vitamin_d']
    if vitamin_d < 20:
        age_modifier += 1
    elif vitamin_d >= 40:
        age_modifier -= 1
    
    # 6. LDL
    ldl = biomarkers['ldl']
    if ldl < 100:
        age_modifier -= 1
    elif ldl > 160:
        age_modifier += 2
    
    biological_age = chronological_age + age_modifier
    biological_age = max(18, min(biological_age, chronological_age + 20))
    
    return {
        "biological_age": round(biological_age, 1),
        "inflammation_score": round(inflammation_score, 1),
        "metabolic_health_score": round(metabolic_score, 1),
        "cardiovascular_risk": cv_risk
    }