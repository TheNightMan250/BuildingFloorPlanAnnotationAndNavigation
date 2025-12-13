from typing import List, Tuple, Optional, Dict, Set
import math
from domain.buildings.floor import Floor
from domain.buildings.room import Room
from domain.buildings.stair import Stair
from domain.buildings.pathway import Pathway


class BuildingGraph:
    def __init__(self, floors: List[Floor], stairs: List[Stair], pathways: Optional[List[Pathway]] = None):
        self.floors = floors
        self.stairs = stairs
        self.pathways = pathways or []
        self._floor_index: Dict[int, Floor] = {floor.floor_id: floor for floor in floors if floor.floor_id}
        self._stair_index: Dict[Tuple[int, int], List[Stair]] = {}
        self._pathways_by_floor: Dict[int, List[Pathway]] = {}
        self._adj: Dict[Tuple[int, float, float], List[Tuple[int, float, float]]] = {}
        self._build_stair_index()
        self._build_pathway_index()
        self._build_adjacency()
    
    def _build_stair_index(self):
        for stair in self.stairs:
            key = (min(stair.from_floor_id, stair.to_floor_id), 
                   max(stair.from_floor_id, stair.to_floor_id))
            if key not in self._stair_index:
                self._stair_index[key] = []
            self._stair_index[key].append(stair)

    def _build_pathway_index(self):
        self._pathways_by_floor = {}
        for p in self.pathways:
            self._pathways_by_floor.setdefault(p.floor_id, []).append(p)

    def _node_key(self, floor_id: int, x: float, y: float) -> Tuple[int, float, float]:
        return (floor_id, round(float(x), 2), round(float(y), 2))

    def _distance(self, a: Tuple[int, float, float], b: Tuple[int, float, float]) -> float:
        _, ax, ay = a
        _, bx, by = b
        return math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)

    def _closest_point_on_segment(self, px: float, py: float,
                                 ax: float, ay: float,
                                 bx: float, by: float) -> Tuple[float, float, float]:
        abx = bx - ax
        aby = by - ay
        ab_len2 = abx * abx + aby * aby
        if ab_len2 <= 0.0:
            return ax, ay, 0.0
        apx = px - ax
        apy = py - ay
        t = (apx * abx + apy * aby) / ab_len2
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        return ax + t * abx, ay + t * aby, t

    def _nearest_pathway_attachment(self, floor_id: int, x: float, y: float) -> Optional[Tuple[Tuple[int, float, float], Tuple[int, float, float], Tuple[int, float, float]]]:
        best = None
        best_dist = float('inf')
        for p in self._pathways_by_floor.get(floor_id, []):
            if not p.points or len(p.points) < 2:
                continue
            for i in range(len(p.points) - 1):
                ax, ay = p.points[i]
                bx, by = p.points[i + 1]
                proj_x, proj_y, _ = self._closest_point_on_segment(float(x), float(y), float(ax), float(ay), float(bx), float(by))
                dx = float(x) - proj_x
                dy = float(y) - proj_y
                d = math.sqrt(dx * dx + dy * dy)
                if d < best_dist:
                    best_dist = d
                    proj_node = self._node_key(floor_id, proj_x, proj_y)
                    a_node = self._node_key(floor_id, ax, ay)
                    b_node = self._node_key(floor_id, bx, by)
                    best = (proj_node, a_node, b_node)
        return best

    def _get_pathway_nodes_for_floor(self, floor_id: int) -> List[Tuple[int, float, float]]:
        nodes: List[Tuple[int, float, float]] = []
        for p in self._pathways_by_floor.get(floor_id, []):
            for x, y in p.points:
                nodes.append(self._node_key(floor_id, x, y))
        return nodes

    def _nearest_node(self, node: Tuple[int, float, float], candidates: List[Tuple[int, float, float]]) -> Optional[Tuple[int, float, float]]:
        if not candidates:
            return None
        return min(candidates, key=lambda c: self._distance(node, c))

    def _add_edge(self, a: Tuple[int, float, float], b: Tuple[int, float, float]):
        self._adj.setdefault(a, [])
        self._adj.setdefault(b, [])
        if b not in self._adj[a]:
            self._adj[a].append(b)
        if a not in self._adj[b]:
            self._adj[b].append(a)

    def _build_adjacency(self):
        self._adj = {}

        # Pathway edges (per floor)
        for p in self.pathways:
            if not p.points or len(p.points) < 2:
                continue
            pts = [self._node_key(p.floor_id, x, y) for x, y in p.points]
            for i in range(len(pts) - 1):
                self._add_edge(pts[i], pts[i + 1])

        # Ensure room nodes exist; connect rooms to pathway network if present
        for floor in self.floors:
            if not floor.floor_id:
                continue
            floor_id = floor.floor_id
            pathway_nodes = self._get_pathway_nodes_for_floor(floor_id)
            rooms = floor.get_all_rooms()
            
            for room in rooms:
                cx, cy = room.get_center()
                room_node = self._node_key(floor_id, cx, cy)
                self._adj.setdefault(room_node, [])
                if pathway_nodes:
                    attach = self._nearest_pathway_attachment(floor_id, float(cx), float(cy))
                    if attach:
                        proj_node, a_node, b_node = attach
                        self._add_edge(room_node, proj_node)
                        self._add_edge(proj_node, a_node)
                        self._add_edge(proj_node, b_node)
            
            # stair nodes on this floor connect to pathway network if present
            for stair in floor.stairs:
                if stair.from_floor_id != floor_id and stair.to_floor_id != floor_id:
                    continue
                sx, sy = stair.position
                stair_node = self._node_key(floor_id, sx, sy)
                self._adj.setdefault(stair_node, [])
                if pathway_nodes:
                    attach = self._nearest_pathway_attachment(floor_id, float(sx), float(sy))
                    if attach:
                        proj_node, a_node, b_node = attach
                        self._add_edge(stair_node, proj_node)
                        self._add_edge(proj_node, a_node)
                        self._add_edge(proj_node, b_node)

            # Fallback: if no pathways exist on this floor, keep old behavior (dense room connectivity)
            if not pathway_nodes:
                room_nodes = [self._node_key(floor_id, *r.get_center()) for r in rooms]
                stair_nodes = [self._node_key(floor_id, s.position[0], s.position[1]) for s in floor.stairs]
                all_nodes = room_nodes + stair_nodes
                for a in all_nodes:
                    self._adj.setdefault(a, [])
                    for b in all_nodes:
                        if a != b:
                            self._add_edge(a, b)

        # Cross-floor stair connections
        for stair in self.stairs:
            a = self._node_key(stair.from_floor_id, stair.position[0], stair.position[1])
            b = self._node_key(stair.to_floor_id, stair.position[0], stair.position[1])
            self._add_edge(a, b)
    
    def get_floor(self, floor_id: int) -> Optional[Floor]:
        return self._floor_index.get(floor_id)
    
    def get_rooms_on_floor(self, floor_id: int) -> List[Room]:
        floor = self.get_floor(floor_id)
        return floor.get_all_rooms() if floor else []
    
    def get_stairs_between(self, floor_id_1: int, floor_id_2: int) -> List[Stair]:
        key = (min(floor_id_1, floor_id_2), max(floor_id_1, floor_id_2))
        return self._stair_index.get(key, [])
    
    def get_connected_floors(self, floor_id: int) -> List[int]:
        connected: Set[int] = set()
        for stair in self.stairs:
            if stair.from_floor_id == floor_id:
                connected.add(stair.to_floor_id)
            elif stair.to_floor_id == floor_id:
                connected.add(stair.from_floor_id)
        return list(connected)
    
    def get_all_nodes(self) -> Dict[Tuple[int, float, float], Tuple[int, float, float]]:
        nodes: Dict[Tuple[int, float, float], Tuple[int, float, float]] = {}
        for floor in self.floors:
            if not floor.floor_id:
                continue
            for room in floor.get_all_rooms():
                center = room.get_center()
                node_key = (floor.floor_id, center[0], center[1])
                nodes[node_key] = (floor.floor_id, center[0], center[1])
            for stair in floor.stairs:
                if stair.from_floor_id == floor.floor_id:
                    node_key = (floor.floor_id, stair.position[0], stair.position[1])
                    nodes[node_key] = (floor.floor_id, stair.position[0], stair.position[1])
        return nodes
    
    def get_neighbors(self, node: Tuple[int, float, float]) -> List[Tuple[int, float, float]]:
        key = self._node_key(node[0], node[1], node[2])
        return self._adj.get(key, [])
    
    def get_room_node(self, room_id: int) -> Optional[Tuple[int, float, float]]:
        for floor in self.floors:
            if not floor.floor_id:
                continue
            for room in floor.get_all_rooms():
                if room.room_id == room_id:
                    center = room.get_center()
                    return self._node_key(floor.floor_id, center[0], center[1])
        return None
    
    def get_stair_cost(self, from_node: Tuple[int, float, float], 
                      to_node: Tuple[int, float, float]) -> float:
        from_floor_id, _, _ = from_node
        to_floor_id, _, _ = to_node
        
        if from_floor_id == to_floor_id:
            return 1.0
        
        stairs = self.get_stairs_between(from_floor_id, to_floor_id)
        if stairs:
            return 10.0
        
        return float('inf')

