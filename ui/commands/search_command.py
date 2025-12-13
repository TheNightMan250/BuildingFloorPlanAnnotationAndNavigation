from ui.commands.command import Command
from controllers.search_controller import SearchController
from typing import List
from domain.buildings.room import Room


class SearchCommand(Command):
    def __init__(self, search_controller: SearchController, query: str):
        self.search_controller = search_controller
        self.query = query
        self.results: List[Room] = []
    
    def execute(self):
        self.results = self.search_controller.search_rooms(self.query)
        return self.results
    
    def undo(self):
        self.results = []

