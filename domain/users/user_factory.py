from domain.users.user import User
from domain.users.admin_user import AdminUser
from domain.users.guest_user import GuestUser
from domain.users.map_creator import MapCreator


class UserFactory:
    @staticmethod
    def create_user(user_type: str, user_id: int, username: str, email: str) -> User:
        if user_type == "admin":
            return AdminUser(user_id, username, email)
        elif user_type == "creator":
            return MapCreator(user_id, username, email)
        elif user_type == "guest":
            return GuestUser(user_id, username, email)
        else:
            raise ValueError(f"Unknown user type: {user_type}")

