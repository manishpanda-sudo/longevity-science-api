from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    biomarker_uploads = relationship("BiomarkerUpload", back_populates="user", cascade="all, delete-orphan")

class BiomarkerUpload(Base):
    __tablename__ = "biomarker_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")  # processing/completed/failed
    
    # Relationships
    user = relationship("User", back_populates="biomarker_uploads")
    biomarker_data = relationship("BiomarkerData", back_populates="upload", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="upload", cascade="all, delete-orphan")

class BiomarkerData(Base):
    __tablename__ = "biomarker_data"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("biomarker_uploads.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    cholesterol_total = Column(Float)
    hdl = Column(Float)
    ldl = Column(Float)
    triglycerides = Column(Float)
    glucose = Column(Float)
    crp = Column(Float)  # C-reactive protein (inflammation marker)
    vitamin_d = Column(Float)
    
    # Relationships
    upload = relationship("BiomarkerUpload", back_populates="biomarker_data")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("biomarker_uploads.id"), nullable=False)
    biological_age = Column(Float)
    chronological_age = Column(Float)
    inflammation_score = Column(Float)
    metabolic_health_score = Column(Float)
    cardiovascular_risk = Column(String)  # low/medium/high
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    upload = relationship("BiomarkerUpload", back_populates="analysis_results")