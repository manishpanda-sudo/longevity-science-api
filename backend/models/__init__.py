from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models to make them available when importing from models
from models.users import User, UserRole
from models.biomarkers import BiomarkerUpload, BiomarkerData, AnalysisResult

__all__ = [
    "Base",
    "User",
    "UserRole",
    "BiomarkerUpload",
    "BiomarkerData",
    "AnalysisResult",
]