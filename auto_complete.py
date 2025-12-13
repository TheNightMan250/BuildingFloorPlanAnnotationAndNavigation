"""
Smart auto-completion engine for drawing assistance.
"""
from PyQt6.QtCore import QPointF, QRectF
from typing import List, Optional, Union, Dict, Any
import math
from core.state_encoder import encode_state


class AutoCompleteEngine:
    """Handles intelligent shape completion suggestions."""
    
    def __init__(self):
        self.suggestions = []
        self.tolerance = 5  # pixels - reduced from 10 for better responsiveness
        self.angle_threshold_deg = 20  # allowable deviation from 90 degrees
        self.geo_w = 0.4
        self.pat_w = 0.3
        self.nn_w = 0.3
    
    def suggest_rectangle(self, points: List[QPointF]) -> Optional[QRectF]:
        """Suggest a rectangle from 2 points."""
        if len(points) < 2:
            return None
        p1, p2 = points[0], points[1]
        left = min(p1.x(), p2.x())
        right = max(p1.x(), p2.x())
        top = min(p1.y(), p2.y())
        bottom = max(p1.y(), p2.y())
        if abs(right - left) < self.tolerance or abs(bottom - top) < self.tolerance:
            return None
        return QRectF(left, top, right - left, bottom - top)
    
    def suggest_l_shape(self, points: List[QPointF]) -> Optional[List[QPointF]]:
        """
        Suggest an L-shape from points.
        Returns list of vertices if suggestion is valid, None otherwise.
        """
        if len(points) < 3:
            return None
        
        # Use the last bend to evaluate the L
        p1, p2, p3 = points[-3], points[-2], points[-1]
        
        # Check if points form a near right angle
        v1 = QPointF(p2.x() - p1.x(), p2.y() - p1.y())
        v2 = QPointF(p3.x() - p2.x(), p3.y() - p2.y())
        
        len_v1 = math.hypot(v1.x(), v1.y())
        len_v2 = math.hypot(v2.x(), v2.y())
        if len_v1 < self.tolerance or len_v2 < self.tolerance:
            return None
        
        dot_product = v1.x() * v2.x() + v1.y() * v2.y()
        cos_angle = dot_product / (len_v1 * len_v2)
        # Clamp numerical noise
        cos_angle = max(min(cos_angle, 1.0), -1.0)
        angle_deg = math.degrees(math.acos(cos_angle))
        
        if abs(angle_deg - 90.0) <= self.angle_threshold_deg:
            return self._rectangle_polygon(points[0], points[-1])
        
        return None
    
    def get_suggestion(
        self, points: List[QPointF], tool_type: str = "room", context: Optional[Dict[str, Any]] = None
    ) -> Optional[Union[QRectF, List[QPointF]]]:
        """
        Get suggestion based on current points and tool type.
        Returns suggestion object (QRectF for rectangle, list of points for shapes).
        """
        context = context or {}
        previous_rooms = context.get("previous_rooms") or []
        pattern_learner = context.get("pattern_learner")
        scene_width = context.get("scene_width", 1.0)
        scene_height = context.get("scene_height", 1.0)

        geo_center = None
        pat_center = None
        nn_center = None

        if tool_type in ("room", "draw_room"):
            if len(points) == 2:
                rect = self.suggest_rectangle(points)
                if rect:
                    geo_center = rect.center()
            if len(points) >= 3:
                poly = self.suggest_l_shape(points)
                if poly:
                    xs = [p.x() for p in poly]
                    ys = [p.y() for p in poly]
                    geo_center = QPointF(sum(xs) / len(xs), sum(ys) / len(ys))

        # Pattern prediction
        if pattern_learner and len(previous_rooms) >= 2:
            verts = [r.get_vertices() for r in previous_rooms[-2:]]
            pat_suggestions = pattern_learner.suggest_positions(verts, num_suggestions=1)
            if pat_suggestions:
                x, y = pat_suggestions[0]
                pat_center = QPointF(x, y)

            # NN prediction using DQN
            try:
                last = previous_rooms[-1].get_vertices()
                prev = previous_rooms[-2].get_vertices()
                last_cx, last_cy = self._center_from_vertices(last)
                prev_cx, prev_cy = self._center_from_vertices(prev)
                avg_angle = pattern_learner.performance_metrics.get("direction_r2", 0) * 360
                state = encode_state(
                    (last_cx, last_cy),
                    (prev_cx, prev_cy),
                    avg_angle=avg_angle,
                    pattern_count=len(pattern_learner.patterns),
                    grid_w=scene_width,
                    grid_h=scene_height,
                    device=pattern_learner.dqn.device,
                )
                nn_vec = pattern_learner.dqn.act(state)
                nx = last_cx + float(nn_vec[0].item()) * scene_width * 0.05
                ny = last_cy + float(nn_vec[1].item()) * scene_height * 0.05
                nn_center = QPointF(nx, ny)
            except Exception:
                pass

        combined = self._combine_centers(geo_center, pat_center, nn_center)
        if combined:
            if tool_type in ("room", "draw_room"):
                size = 40
                return QRectF(combined.x() - size / 2, combined.y() - size / 2, size, size)
        return None
    
    def snap_to_grid(self, point: QPointF, grid_size: int = 10) -> QPointF:
        """Snap point to grid."""
        x = round(point.x() / grid_size) * grid_size
        y = round(point.y() / grid_size) * grid_size
        return QPointF(x, y)
    
    def snap_to_existing(self, point: QPointF, existing_points: List[QPointF]) -> QPointF:
        """Snap point to nearby existing points."""
        for existing in existing_points:
            distance = math.sqrt((point.x() - existing.x())**2 + (point.y() - existing.y())**2)
            if distance < self.tolerance:
                return existing
        return point

    def _rectangle_polygon(self, first: QPointF, last: QPointF) -> Optional[List[QPointF]]:
        """Create axis-aligned rectangle polygon from first and last points."""
        width = abs(last.x() - first.x())
        height = abs(last.y() - first.y())
        if width < self.tolerance or height < self.tolerance:
            return None
        return [
            QPointF(first.x(), first.y()),
            QPointF(last.x(), first.y()),
            QPointF(last.x(), last.y()),
            QPointF(first.x(), last.y()),
        ]

    def _combine_centers(self, geo, pat, nn):
        centers = []
        weights = []
        if geo:
            centers.append(geo)
            weights.append(self.geo_w)
        if pat:
            centers.append(pat)
            weights.append(self.pat_w)
        if nn:
            centers.append(nn)
            weights.append(self.nn_w)
        if not centers:
            return None
        total = sum(weights)
        wx = sum(c.x() * w for c, w in zip(centers, weights)) / total
        wy = sum(c.y() * w for c, w in zip(centers, weights)) / total
        return QPointF(wx, wy)

    def _center_from_vertices(self, verts):
        if not verts:
            return (0.0, 0.0)
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

