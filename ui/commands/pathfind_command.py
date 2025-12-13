from ui.commands.command import Command
from controllers.map_controller import MapController
from typing import List, Tuple, Optional


class PathfindCommand(Command):
    def __init__(self, map_controller: MapController, start: Tuple[float, float],
                 end: Tuple[float, float], floor_id: int):
        self.map_controller = map_controller
        self.start = start
        self.end = end
        self.floor_id = floor_id
        self.path: Optional[List[Tuple[float, float]]] = None
    
    def execute(self):
        self.path = self.map_controller.get_path(self.start, self.end, self.floor_id)
        return self.path
    
    def undo(self):
        self.path = None

