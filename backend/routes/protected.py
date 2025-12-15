from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import User, BiomarkerUpload
from dependencies import get_db, get_current_user,get_permission_checker
from rbac import PermissionChecker, PermissionRegistry, Resource, ResourceOwnershipValidator

router = APIRouter(prefix="/protected", tags=["Protected"])

@router.get("/user")
def protected_user_route(
    current_user: User = Depends(get_current_user),
    checker: PermissionChecker = Depends(get_permission_checker)
):
    """Get current user profile"""
    checker.require_permission(PermissionRegistry.USER_READ_OWN_PROFILE)
    
    return {
        "message": "This is a protected route for authenticated users",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role.value
        }
    }

@router.get("/dashboard")
def user_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    uploads = db.query(BiomarkerUpload).filter(BiomarkerUpload.user_id == current_user.id).all()
    
    return {
        "message": f"Welcome to your dashboard, {current_user.full_name}!",
        "user_id": current_user.id,
        "role": current_user.role.value,
        "total_uploads": len(uploads),
        "uploads": [
            {
                "id": upload.id,
                "filename": upload.filename,
                "upload_date": upload.upload_date.isoformat(),
                "status": upload.status
            }
            for upload in uploads
        ]
    }