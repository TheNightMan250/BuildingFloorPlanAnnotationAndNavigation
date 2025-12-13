from typing import Optional
from domain.users.user import User
from domain.users.user_manager import UserManager
from data.repositories.user_repo import IUserRepository


class AuthController:
    def __init__(self, user_manager: UserManager, user_repo: IUserRepository):
        self.user_manager = user_manager
        self.user_repo = user_repo
    
    def login(self, username: str) -> bool:
        user = self.user_repo.find_by_username(username)
        if user:
            self.user_manager.set_current_user(user)
            return True
        return False
    
    def logout(self):
        self.user_manager.logout()
    
    def get_current_user(self) -> Optional[User]:
        return self.user_manager.get_current_user()
    
    def register_user(self, user_type: str, username: str, email: str) -> User:
        existing_users = []
        for user_id in range(1, 1000):
            user = self.user_repo.find_by_id(user_id)
            if user:
                existing_users.append(user)
        user_id = max([u.user_id for u in existing_users], default=0) + 1
        user = self.user_manager.create_user(user_type, user_id, username, email)
        self.user_repo.save(user)
        return user

