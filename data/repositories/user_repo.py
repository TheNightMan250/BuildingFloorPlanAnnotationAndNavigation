from abc import ABC, abstractmethod
from typing import Optional, List
from domain.users.user import User


class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


class UserRepository(IUserRepository):
    def __init__(self):
        self._users: dict = {}
        self._username_index: dict = {}
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)
    
    def find_by_username(self, username: str) -> Optional[User]:
        return self._username_index.get(username)
    
    def save(self, user: User) -> User:
        if user.user_id:
            self._users[user.user_id] = user
        else:
            new_id = max(self._users.keys(), default=0) + 1
            user.user_id = new_id
            self._users[new_id] = user
        
        self._username_index[user.username] = user
        return user
    
    def delete(self, user_id: int) -> bool:
        user = self._users.get(user_id)
        if user:
            del self._users[user_id]
            if user.username in self._username_index:
                del self._username_index[user.username]
            return True
        return False
