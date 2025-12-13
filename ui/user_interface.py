from PyQt6.QtWidgets import QMainWindow
from typing import Optional
from controllers.auth_controller import AuthController
from controllers.map_controller import MapController
from controllers.search_controller import SearchController
from controllers.navigation_controller import NavigationController


class UserInterface:
    def __init__(self, auth_controller: AuthController, map_controller: MapController,
                 search_controller: SearchController, navigation_controller: NavigationController):
        self.auth_controller = auth_controller
        self.map_controller = map_controller
        self.search_controller = search_controller
        self.navigation_controller = navigation_controller
        self.main_window: Optional[QMainWindow] = None
    
    def set_main_window(self, main_window: QMainWindow):
        self.main_window = main_window
    
    def get_auth_controller(self) -> AuthController:
        return self.auth_controller
    
    def get_map_controller(self) -> MapController:
        return self.map_controller
    
    def get_search_controller(self) -> SearchController:
        return self.search_controller
    
    def get_navigation_controller(self) -> NavigationController:
        return self.navigation_controller

