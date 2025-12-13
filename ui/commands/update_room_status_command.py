from ui.commands.command import Command
from controllers.map_controller import MapController
from domain.buildings.room import Room


class UpdateRoomStatusCommand(Command):
    def __init__(self, map_controller: MapController, room: Room, new_status: str):
        self.map_controller = map_controller
        self.room = room
        self.new_status = new_status
        self.old_status = room.room_type
    
    def execute(self):
        self.room.room_type = self.new_status
        self.map_controller.room_repo.save(self.room)
        return True
    
    def undo(self):
        self.room.room_type = self.old_status
        self.map_controller.room_repo.save(self.room)
