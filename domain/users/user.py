from abc import ABC, abstractmethod
from typing import List, Optional


class User(ABC):
    def __init__(self, user_id: int, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.permissions = []
    
    @abstractmethod
    def can_create_map(self) -> bool:
        pass
    
    @abstractmethod
    def can_approve_map(self) -> bool:
        pass
    
    @abstractmethod
    def can_delete_map(self) -> bool:
        pass
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

