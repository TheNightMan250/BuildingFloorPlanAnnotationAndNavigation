import math
from typing import List, Tuple, Optional, Dict
from domain.pathfinder.pathfinder import Pathfinder
from domain.buildings.room import Room
from domain.pathfinder.building_graph import BuildingGraph


class DijkstraPathfinder(Pathfinder):
    def __init__(self):
        self.grid_size = 10.0
    
    def find_path(self, start: Tuple[float, float], end: Tuple[float, float], 
                  rooms: List[Room]) -> Optional[List[Tuple[float, float]]]:
        if not rooms:
            return [start, end]
        
        graph = self._build_graph(start, end, rooms)
        distances: Dict[Tuple[float, float], float] = {start: 0.0}
        previous: Dict[Tuple[float, float], Optional[Tuple[float, float]]] = {start: None}
        unvisited = {start}
        visited = set()
        
        while unvisited:
            current = min(unvisited, key=lambda x: distances.get(x, float('inf')))
            unvisited.remove(current)
            visited.add(current)
            
            if current == end:
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = previous.get(node)
                return list(reversed(path))
            
            for neighbor in graph.get(current, []):
                if neighbor in visited:
                    continue
                alt = distances[current] + self._distance(current, neighbor)
                if alt < distances.get(neighbor, float('inf')):
                    distances[neighbor] = alt
                    previous[neighbor] = current
                    unvisited.add(neighbor)
        
        return None
    
    def _build_graph(self, start: Tuple[float, float], end: Tuple[float, float], 
                     rooms: List[Room]) -> Dict[Tuple[float, float], List[Tuple[float, float]]]:
        graph: Dict[Tuple[float, float], List[Tuple[float, float]]] = {}
        nodes = [start, end]
        
        for room in rooms:
            center = room.get_center()
            nodes.append(center)
        
        for node in nodes:
            graph[node] = []
            for other in nodes:
                if node != other and not self._intersects_room(node, other, rooms):
                    graph[node].append(other)
        
        return graph
    
    def _intersects_room(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                        rooms: List[Room]) -> bool:
        for room in rooms:
            if self._line_intersects_polygon(p1, p2, room.vertices):
                return True
        return False
    
    def _line_intersects_polygon(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                                 vertices: List[List[float]]) -> bool:
        for i in range(len(vertices)):
            v1 = tuple(vertices[i])
            v2 = tuple(vertices[(i + 1) % len(vertices)])
            if self._line_intersect(p1, p2, v1, v2):
                return True
        return False
    
    def _line_intersect(self, p1: Tuple[float, float], p2: Tuple[float, float],
                       p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    def find_multi_floor_path(self, start_room_id: int, end_room_id: int,
                              building_graph: BuildingGraph) -> Optional[List[Tuple[int, float, float]]]:
        start_node = building_graph.get_room_node(start_room_id)
        end_node = building_graph.get_room_node(end_room_id)
        
        if not start_node or not end_node:
            return None
        
        start_room = None
        end_room = None
        for floor in building_graph.floors:
            if not floor.floor_id:
                continue
            for room in floor.get_all_rooms():
                if room.room_id == start_room_id:
                    start_room = room
                if room.room_id == end_room_id:
                    end_room = room
        
        if not start_room or not end_room:
            return None
        
        distances: Dict[Tuple[int, float, float], float] = {start_node: 0.0}
        previous: Dict[Tuple[int, float, float], Optional[Tuple[int, float, float]]] = {start_node: None}
        unvisited = {start_node}
        visited = set()
        
        while unvisited:
            current = min(unvisited, key=lambda x: distances.get(x, float('inf')))
            unvisited.remove(current)
            visited.add(current)
            
            if current == end_node:
                path = []
                node = end_node
                while node is not None:
                    path.append(node)
                    node = previous.get(node)
                return list(reversed(path))
            
            neighbors = building_graph.get_neighbors(current)
            
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                
                neighbor_floor_id, nx, ny = neighbor
                current_floor_id, cx, cy = current
                
                if current_floor_id == neighbor_floor_id:
                    cost = self._distance((cx, cy), (nx, ny))
                else:
                    cost = building_graph.get_stair_cost(current, neighbor)
                
                alt = distances[current] + cost
                if alt < distances.get(neighbor, float('inf')):
                    distances[neighbor] = alt
                    previous[neighbor] = current
                    unvisited.add(neighbor)
        
        return None
    
    def get_algorithm_name(self) -> str:
        return "Dijkstra"

