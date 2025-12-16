from fastapi import Depends, HTTPException, status

from dependencies.auth import get_current_user
from rbac import PermissionChecker, Permission, Action, Resource
from models import User


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