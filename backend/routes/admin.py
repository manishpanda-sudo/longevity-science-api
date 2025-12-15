from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models import User, UserRole, BiomarkerUpload, AnalysisResult
from dependencies import get_db, get_current_user, get_permission_checker, require_admin
from routes.auth import UserResponse
from rbac import PermissionChecker, PermissionRegistry, Action, Resource, ResourceOwnershipValidator

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    checker: PermissionChecker = Depends(require_admin())
):
    """Get all users - Admin only"""
    checker.require_permission(PermissionRegistry.ADMIN_VIEW_ALL_USERS)
    
    users = db.query(User).all()
    return users

@router.get("/stats")
def admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    checker: PermissionChecker = Depends(require_admin())
):
    """Get system statistics - Admin only"""
    checker.require_permission(PermissionRegistry.ADMIN_MANAGE_SYSTEM)
    
    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.role == UserRole.ADMIN).count()
    total_regular_users = db.query(User).filter(User.role == UserRole.USER).count()
    total_uploads = db.query(BiomarkerUpload).count()
    
    return {
        "message": "Admin statistics",
        "admin": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name
        },
        "stats": {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_regular_users": total_regular_users,
            "total_uploads": total_uploads
        }
    }

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    checker: PermissionChecker = Depends(require_admin())
):
    """Delete a user - Admin only"""
    checker.require_permission(PermissionRegistry.ADMIN_DELETE_USERS)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.email} deleted successfully"}

@router.get("/all-uploads")
def get_all_uploads(
    db: Session = Depends(get_db),
    checker: PermissionChecker = Depends(require_admin())
):
    """Get all uploads from all users - Admin only"""
    checker.require_permission(PermissionRegistry.ADMIN_VIEW_ALL_UPLOADS)
    
    uploads = db.query(BiomarkerUpload).order_by(BiomarkerUpload.upload_date.desc()).all()
    
    result = []
    for upload in uploads:
        user = db.query(User).filter(User.id == upload.user_id).first()
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.upload_id == upload.id
        ).first()
        
        result.append({
            "id": upload.id,
            "filename": upload.filename,
            "upload_date": upload.upload_date.isoformat(),
            "status": upload.status,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            },
            "analysis": {
                "biological_age": analysis.biological_age,
                "chronological_age": analysis.chronological_age,
                "age_difference": analysis.chronological_age - analysis.biological_age,
                "inflammation_score": analysis.inflammation_score,
                "metabolic_health_score": analysis.metabolic_health_score,
                "cardiovascular_risk": analysis.cardiovascular_risk
            } if analysis else None
        })
    
    return {
        "total_uploads": len(result),
        "uploads": result
    }