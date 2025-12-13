from ui.commands.command import Command
from controllers.navigation_controller import NavigationController
from typing import List, Tuple, Optional, Dict


class NavigateCommand(Command):
    def __init__(self, navigation_controller: NavigationController):
        self.navigation_controller = navigation_controller
        self.path: Optional[List[Tuple[int, float, float]]] = None
        self.path_by_floor: Dict[int, List[Tuple[float, float]]] = {}
    
    def execute(self):
        self.path = self.navigation_controller.get_navigation_path()
        if self.path:
            self.path_by_floor = self.navigation_controller.get_path_by_floor()
        return self.path is not None
    
    def undo(self):
        self.path = None
        self.path_by_floor = {}
    
    def get_path(self) -> Optional[List[Tuple[int, float, float]]]:
        return self.path
    
    def get_path_by_floor(self) -> Dict[int, List[Tuple[float, float]]]:
        return self.path_by_floor

