from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from models import User, BiomarkerUpload
from dependencies import get_db, get_current_user, get_permission_checker
from rbac import PermissionChecker, PermissionRegistry

router = APIRouter()


@router.delete("/{upload_id}")
def delete_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    checker: PermissionChecker = Depends(get_permission_checker)
):
    """Delete an upload and all associated data"""

    checker.require_permission(PermissionRegistry.USER_DELETE_OWN_UPLOADS)
    
    upload = db.query(BiomarkerUpload).filter(BiomarkerUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    if upload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(upload)
    db.commit()
    
    return {"message": "Upload deleted successfully"}