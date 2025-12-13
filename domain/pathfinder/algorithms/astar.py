import math
from typing import List, Tuple, Optional, Dict
from domain.pathfinder.pathfinder import Pathfinder
from domain.buildings.room import Room
from domain.pathfinder.building_graph import BuildingGraph


class AStarPathfinder(Pathfinder):
    def __init__(self):
        self.grid_size = 10.0
    
    def find_path(self, start: Tuple[float, float], end: Tuple[float, float], 
                  rooms: List[Room]) -> Optional[List[Tuple[float, float]]]:
        if not rooms:
            return [start, end]
        
        graph = self._build_graph(start, end, rooms)
        open_set = {start}
        closed_set = set()
        g_score: Dict[Tuple[float, float], float] = {start: 0.0}
        f_score: Dict[Tuple[float, float], float] = {start: self._heuristic(start, end)}
        came_from: Dict[Tuple[float, float], Optional[Tuple[float, float]]] = {start: None}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end:
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = came_from.get(node)
                return list(reversed(path))
            
            open_set.remove(current)
            closed_set.add(current)
            
            for neighbor in graph.get(current, []):
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + self._distance(current, neighbor)
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g >= g_score.get(neighbor, float('inf')):
                    continue
                
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = g_score[neighbor] + self._heuristic(neighbor, end)
        
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
    
    def _heuristic(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return self._distance(p1, p2)
    
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
        
        open_set = {start_node}
        closed_set = set()
        g_score: Dict[Tuple[int, float, float], float] = {start_node: 0.0}
        f_score: Dict[Tuple[int, float, float], float] = {
            start_node: self._node_heuristic(start_node, end_node)
        }
        came_from: Dict[Tuple[int, float, float], Optional[Tuple[int, float, float]]] = {start_node: None}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end_node:
                path = []
                node = end_node
                while node is not None:
                    path.append(node)
                    node = came_from.get(node)
                return list(reversed(path))
            
            open_set.remove(current)
            closed_set.add(current)
            
            neighbors = building_graph.get_neighbors(current)
            
            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue
                
                neighbor_floor_id, nx, ny = neighbor
                current_floor_id, cx, cy = current
                
                if current_floor_id == neighbor_floor_id:
                    cost = self._distance((cx, cy), (nx, ny))
                else:
                    cost = building_graph.get_stair_cost(current, neighbor)
                
                tentative_g = g_score[current] + cost
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g >= g_score.get(neighbor, float('inf')):
                    continue
                
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = g_score[neighbor] + self._node_heuristic(neighbor, end_node)
        
        return None
    
    def _node_heuristic(self, node1: Tuple[int, float, float], node2: Tuple[int, float, float]) -> float:
        _, x1, y1 = node1
        _, x2, y2 = node2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def get_algorithm_name(self) -> str:
        return "A*"

