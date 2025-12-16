from typing import Dict, Any
import pandas as pd


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