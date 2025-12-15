from typing import Set, Dict
from models import UserRole
from rbac.permissions import Permission, PermissionRegistry


class Role:
    """Base class for all roles"""
    
    def __init__(self, name: str, permissions: Set[Permission]):
        self.name = name
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has a specific permission"""
        return permission in self.permissions
    
    def has_action_on_resource(self, action, resource) -> bool:
        """Check if role can perform action on resource"""
        permission = Permission(action, resource)
        return self.has_permission(permission)
    
    def __repr__(self):
        return f"Role(name={self.name}, permissions={len(self.permissions)})"


class UserRoleDefinition(Role):
    """Regular user role with basic permissions"""
    
    def __init__(self):
        permissions = {
            # Own profile
            PermissionRegistry.USER_READ_OWN_PROFILE,
            PermissionRegistry.USER_UPDATE_OWN_PROFILE,
            
            # Own uploads
            PermissionRegistry.USER_UPLOAD_BIOMARKER,
            PermissionRegistry.USER_READ_OWN_UPLOADS,
            PermissionRegistry.USER_DELETE_OWN_UPLOADS,
            
            # Own data
            PermissionRegistry.USER_READ_OWN_DATA,
            PermissionRegistry.USER_EXPORT_OWN_DATA,
            
            # Own results
            PermissionRegistry.USER_READ_OWN_RESULTS,
            PermissionRegistry.USER_ANALYZE_OWN_DATA,
            PermissionRegistry.USER_EXPORT_OWN_RESULTS,
        }
        super().__init__(name="USER", permissions=permissions)


class AdminRoleDefinition(Role):
    """Admin role with all permissions"""
    
    def __init__(self):
        # Admin inherits all user permissions plus admin-specific ones
        user_role = UserRoleDefinition()
        admin_permissions = {
            # User management
            PermissionRegistry.ADMIN_MANAGE_USERS,
            PermissionRegistry.ADMIN_VIEW_ALL_USERS,
            PermissionRegistry.ADMIN_DELETE_USERS,
            
            # Upload management
            PermissionRegistry.ADMIN_VIEW_ALL_UPLOADS,
            PermissionRegistry.ADMIN_DELETE_ANY_UPLOAD,
            
            # Data management
            PermissionRegistry.ADMIN_VIEW_ALL_DATA,
            PermissionRegistry.ADMIN_VIEW_ALL_RESULTS,
            
            # System management
            PermissionRegistry.ADMIN_MANAGE_SYSTEM,
            PermissionRegistry.ADMIN_ACCESS_PANEL,
        }
        
        all_permissions = user_role.permissions | admin_permissions
        super().__init__(name="ADMIN", permissions=all_permissions)


class RoleFactory:
    """Factory to create role instances"""
    
    _roles: Dict[UserRole, Role] = {
        UserRole.USER: UserRoleDefinition(),
        UserRole.ADMIN: AdminRoleDefinition(),
    }
    
    @classmethod
    def get_role(cls, user_role: UserRole) -> Role:
        """Get role definition by UserRole enum"""
        return cls._roles.get(user_role)
    
    @classmethod
    def register_role(cls, user_role: UserRole, role_definition: Role):
        """Register a new role (for extensibility)"""
        cls._roles[user_role] = role_definition