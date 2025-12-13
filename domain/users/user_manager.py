from typing import Optional, Dict
from domain.users.user import User
from domain.users.user_factory import UserFactory


class UserManager:
    def __init__(self):
        self._users: Dict[int, User] = {}
        self._current_user: Optional[User] = None
    
    def create_user(self, user_type: str, user_id: int, username: str, email: str) -> User:
        user = UserFactory.create_user(user_type, user_id, username, email)
        self._users[user_id] = user
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)
    
    def set_current_user(self, user: User):
        self._current_user = user
    
    def get_current_user(self) -> Optional[User]:
        return self._current_user
    
    def login(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user:
            self.set_current_user(user)
            return True
        return False
    
    def logout(self):
        self._current_user = None

