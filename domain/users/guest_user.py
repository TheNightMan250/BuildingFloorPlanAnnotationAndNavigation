from domain.users.user import User


class GuestUser(User):
    def __init__(self, user_id: int, username: str, email: str):
        super().__init__(user_id, username, email)
        self.permissions = ["view"]
    
    def can_create_map(self) -> bool:
        return False
    
    def can_approve_map(self) -> bool:
        return False
    
    def can_delete_map(self) -> bool:
        return False

