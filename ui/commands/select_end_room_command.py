from ui.commands.command import Command
from controllers.navigation_controller import NavigationController


class SelectEndRoomCommand(Command):
    def __init__(self, navigation_controller: NavigationController, room_id: int):
        self.navigation_controller = navigation_controller
        self.room_id = room_id
        self.previous_end_room_id = None
    
    def execute(self):
        self.previous_end_room_id = self.navigation_controller.end_room_id
        return self.navigation_controller.set_end_room(self.room_id)
    
    def undo(self):
        if self.previous_end_room_id:
            self.navigation_controller.set_end_room(self.previous_end_room_id)
        else:
            self.navigation_controller.end_room_id = None

