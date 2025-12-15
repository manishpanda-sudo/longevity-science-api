from typing import Optional
from fastapi import HTTPException, status

from models import User, UserRole
from rbac.permissions import Permission, Action, Resource
from rbac.roles import RoleFactory


class PermissionChecker:
    """Main class for checking permissions"""
    
    def __init__(self, user: User):
        self.user = user
        self.role = RoleFactory.get_role(user.role)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        if not self.role:
            return False
        return self.role.has_permission(permission)
    
    def has_action_on_resource(self, action: Action, resource: Resource) -> bool:
        """Check if user can perform action on resource"""
        permission = Permission(action, resource)
        return self.has_permission(permission)
    
    def require_permission(self, permission: Permission):
        """Require permission or raise HTTPException"""
        if not self.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
    
    def require_action_on_resource(self, action: Action, resource: Resource):
        """Require action on resource or raise HTTPException"""
        permission = Permission(action, resource)
        self.require_permission(permission)
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.user.role == UserRole.ADMIN
    
    def can_access_resource(self, resource_owner_id: int, resource: Resource) -> bool:
        """
        Check if user can access a specific resource instance
        - Admins can access any resource
        - Users can only access their own resources
        """
        if self.is_admin():
            return True
        return self.user.id == resource_owner_id


class ResourceOwnershipValidator:
    """Validates ownership of resources"""
    
    @staticmethod
    def validate_ownership(
        user: User,
        resource_owner_id: int,
        resource_type: Resource,
        allow_admin_override: bool = True
    ):
        """
        Validate that user owns the resource or is admin
        
        Args:
            user: The current user
            resource_owner_id: ID of the resource owner
            resource_type: Type of resource being accessed
            allow_admin_override: Whether admins can bypass ownership check
        """
        checker = PermissionChecker(user)
        
        # Admin override
        if allow_admin_override and checker.is_admin():
            return True
        
        # Ownership check
        if user.id != resource_owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to access this {resource_type.value}"
            )
        
        return True