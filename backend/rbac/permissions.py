from enum import Enum
from typing import Set, Dict, List
from dataclasses import dataclass

class Action(Enum):
    """Define all possible actions in the system"""
    # User actions
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    
    # Specific actions
    UPLOAD = "upload"
    DOWNLOAD = "download"
    ANALYZE = "analyze"
    EXPORT = "export"
    
    # Admin actions
    MANAGE_USERS = "manage_users"
    VIEW_ALL = "view_all"
    MANAGE_SYSTEM = "manage_system"


class Resource(Enum):
    """Define all resources in the system"""
    USER = "user"
    BIOMARKER_UPLOAD = "biomarker_upload"
    BIOMARKER_DATA = "biomarker_data"
    ANALYSIS_RESULT = "analysis_result"
    SYSTEM = "system"
    ADMIN_PANEL = "admin_panel"


@dataclass(frozen=True)
class Permission:
    """Represents a single permission (action + resource)"""
    action: Action
    resource: Resource
    
    def __str__(self):
        return f"{self.action.value}:{self.resource.value}"
    
    def __hash__(self):
        return hash((self.action, self.resource))


class PermissionRegistry:
    """Central registry for all permissions"""
    
    # User permissions
    USER_READ_OWN_PROFILE = Permission(Action.READ, Resource.USER)
    USER_UPDATE_OWN_PROFILE = Permission(Action.UPDATE, Resource.USER)
    
    # Biomarker Upload permissions
    USER_UPLOAD_BIOMARKER = Permission(Action.UPLOAD, Resource.BIOMARKER_UPLOAD)
    USER_READ_OWN_UPLOADS = Permission(Action.READ, Resource.BIOMARKER_UPLOAD)
    USER_DELETE_OWN_UPLOADS = Permission(Action.DELETE, Resource.BIOMARKER_UPLOAD)
    
    # Biomarker Data permissions
    USER_READ_OWN_DATA = Permission(Action.READ, Resource.BIOMARKER_DATA)
    USER_EXPORT_OWN_DATA = Permission(Action.EXPORT, Resource.BIOMARKER_DATA)
    
    # Analysis Result permissions
    USER_READ_OWN_RESULTS = Permission(Action.READ, Resource.ANALYSIS_RESULT)
    USER_ANALYZE_OWN_DATA = Permission(Action.ANALYZE, Resource.ANALYSIS_RESULT)
    USER_EXPORT_OWN_RESULTS = Permission(Action.EXPORT, Resource.ANALYSIS_RESULT)
    
    # Admin permissions
    ADMIN_MANAGE_USERS = Permission(Action.MANAGE_USERS, Resource.USER)
    ADMIN_VIEW_ALL_USERS = Permission(Action.VIEW_ALL, Resource.USER)
    ADMIN_DELETE_USERS = Permission(Action.DELETE, Resource.USER)
    
    ADMIN_VIEW_ALL_UPLOADS = Permission(Action.VIEW_ALL, Resource.BIOMARKER_UPLOAD)
    ADMIN_DELETE_ANY_UPLOAD = Permission(Action.DELETE, Resource.BIOMARKER_UPLOAD)
    
    ADMIN_VIEW_ALL_DATA = Permission(Action.VIEW_ALL, Resource.BIOMARKER_DATA)
    ADMIN_VIEW_ALL_RESULTS = Permission(Action.VIEW_ALL, Resource.ANALYSIS_RESULT)
    
    ADMIN_MANAGE_SYSTEM = Permission(Action.MANAGE_SYSTEM, Resource.SYSTEM)
    ADMIN_ACCESS_PANEL = Permission(Action.READ, Resource.ADMIN_PANEL)