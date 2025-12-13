from ui.commands.command import Command
from controllers.auth_controller import AuthController


class LoginCommand(Command):
    def __init__(self, auth_controller: AuthController, username: str):
        self.auth_controller = auth_controller
        self.username = username
        self.was_logged_in = False
    
    def execute(self):
        self.was_logged_in = self.auth_controller.login(self.username)
        return self.was_logged_in
    
    def undo(self):
        if self.was_logged_in:
            self.auth_controller.logout()

