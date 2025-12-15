from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rbac import PermissionChecker, Permission, Action, Resource
from jwt_service import get_jwt_service
from models import User, UserRole

from config import DATABASE_URL


security = HTTPBearer()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    jwt_svc = get_jwt_service()


    
    
    payload = jwt_svc.decode_token(token)
    print(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_permission_checker(
    current_user: User = Depends(get_current_user)
) -> PermissionChecker:
    """Dependency to get permission checker for current user"""
    return PermissionChecker(current_user)


def require_permission(permission: Permission):
    """
    Dependency factory to require specific permission
    
    Usage:
        @router.get("/")
        def my_route(
            checker: PermissionChecker = Depends(require_permission(PermissionRegistry.USER_READ_OWN_PROFILE))
        ):
            pass
    """
    def permission_dependency(
        checker: PermissionChecker = Depends(get_permission_checker)
    ) -> PermissionChecker:
        checker.require_permission(permission)
        return checker
    
    return permission_dependency

def require_action_on_resource(action: Action, resource: Resource):
    """
    Dependency factory to require action on resource
    
    Usage:
        @router.post("/upload")
        def upload(
            checker: PermissionChecker = Depends(require_action_on_resource(Action.UPLOAD, Resource.BIOMARKER_UPLOAD))
        ):
            pass
    """
    def permission_dependency(
        checker: PermissionChecker = Depends(get_permission_checker)
    ) -> PermissionChecker:
        checker.require_action_on_resource(action, resource)
        return checker
    
    return permission_dependency

def require_admin():
    """Dependency to require admin role"""
    def admin_dependency(
        checker: PermissionChecker = Depends(get_permission_checker)
    ) -> PermissionChecker:
        if not checker.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return checker
    
    return admin_dependency


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to ensure current user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user