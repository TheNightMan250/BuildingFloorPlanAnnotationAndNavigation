"""
Drawing canvas widget for floor plan display and editing.
"""
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsPolygonItem,
    QGraphicsPathItem,
)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPixmap,
    QImage,
    QPen,
    QBrush,
    QColor,
    QPolygonF,
    QKeyEvent,
    QPainter,
    QImageReader,
    QPainterPath,
)
from auto_complete import AutoCompleteEngine
from pattern_learner import PatternLearner
from typing import List, Optional, Tuple
import json


class RoomItem(QGraphicsPolygonItem):
    """Graphics item representing a room."""

    def __init__(self, vertices, room_id=None, name="Room", room_type="Room"):
        polygon = QPolygonF([QPointF(v[0], v[1]) for v in vertices])
        super().__init__(polygon)
        self.room_id = room_id
        self.name = name
        self.room_type = room_type

        # Set appearance
        pen = QPen(QColor(0, 100, 200), 2)
        brush = QBrush(QColor(0, 100, 200, 50))
        self.setPen(pen)
        self.setBrush(brush)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPolygonItem.GraphicsItemFlag.ItemIsMovable, False)

    def get_vertices(self):
        """Get vertices as list of [x, y] tuples."""
        polygon = self.polygon()
        return [[point.x(), point.y()] for point in polygon]

    def update_appearance(self, selected=False, is_navigation_start=False, is_navigation_end=False):
        """Update room appearance based on selection and navigation state."""
        if is_navigation_start:
            pen = QPen(QColor(0, 255, 0), 4)  # Green for navigation start
            brush = QBrush(QColor(0, 255, 0, 80))
        elif is_navigation_end:
            pen = QPen(QColor(0, 0, 255), 4)  # Blue for navigation end
            brush = QBrush(QColor(0, 0, 255, 80))
        elif selected:
            pen = QPen(QColor(255, 0, 0), 3)  # Red for selected
            brush = QBrush(QColor(0, 100, 200, 100))
        else:
            pen = QPen(QColor(0, 100, 200), 2)
            brush = QBrush(QColor(0, 100, 200, 50))

        self.setPen(pen)
        self.setBrush(brush)


class SuggestionItem(QGraphicsRectItem):
    """Temporary item for showing auto-completion suggestions."""

    def __init__(self, rect: QRectF):
        super().__init__(rect)
        # Enhanced visibility: thicker line and more visible color
        pen = QPen(QColor(50, 255, 50), 3, Qt.PenStyle.DashLine)  # Brighter green, thicker
        brush = QBrush(QColor(50, 255, 50, 60))  # More visible fill
        self.setPen(pen)
        self.setBrush(brush)
        self.setZValue(1000)  # Always on top


class PolygonSuggestionItem(QGraphicsPolygonItem):
    """Temporary polygon suggestion overlay."""

    def __init__(self, points: List[QPointF]):
        polygon = QPolygonF(points)
        super().__init__(polygon)
        pen = QPen(QColor(50, 255, 50), 3, Qt.PenStyle.DashLine)
        brush = QBrush(QColor(50, 255, 50, 60))
        self.setPen(pen)
        self.setBrush(brush)
        self.setZValue(1000)


class PatternSuggestionMarker(QGraphicsRectItem):
    """Marker for pattern-based room position suggestions with variable size."""

    def __init__(
        self,
        x: float,
        y: float,
        size: float = 20.0,
        room_type: str = "Room",
        confidence: float = 1.0,
        suggested_area: Optional[float] = None,
    ):
        # Variable size based on room type and confidence
        base_size = self._get_size_for_room_type(room_type)
        adjusted_size = base_size * (0.7 + 0.6 * confidence)  # Scale by confidence (0.7x to 1.3x)
        rect = QRectF(x - adjusted_size/2, y - adjusted_size/2, adjusted_size, adjusted_size)
        super().__init__(rect)

        # Color based on confidence
        color = self._get_color_for_confidence(confidence)
        pen = QPen(color, 3)
        brush = QBrush(QColor(color.red(), color.green(), color.blue(), 100))
        self.setPen(pen)
        self.setBrush(brush)
        self.setZValue(1001)  # Above other suggestions
        self.suggestion_pos = (x, y)
        self.room_type = room_type
        self.confidence = confidence
        self.suggested_area = suggested_area
        self.room_half_size = None
        if suggested_area is not None and suggested_area > 0:
            side = suggested_area ** 0.5
            side = max(20.0, min(200.0, side))
            self.room_half_size = side / 2.0

        # Add tooltip for demo
        self.setToolTip(f"{room_type} (Confidence: {confidence:.1%})")

    def _get_size_for_room_type(self, room_type: str) -> float:
        """Get appropriate marker size for different room types."""
        room_sizes = {
            "Lobby": 35.0,
            "Conference": 30.0,
            "Office": 25.0,
            "Kitchen": 28.0,
            "Server": 20.0,
            "Meeting": 26.0,
            "Workspace": 40.0,
            "Lounge": 32.0,
            "Room": 25.0  # Default
        }
        return room_sizes.get(room_type, 25.0)

    def _get_color_for_confidence(self, confidence: float) -> QColor:
        """Get color based on confidence level."""
        if confidence >= 0.8:
            return QColor(255, 100, 100)  # Red for high confidence
        elif confidence >= 0.6:
            return QColor(255, 165, 0)    # Orange for medium confidence
        else:
            return QColor(255, 200, 100)  # Light orange for low confidence


class PathwayItem(QGraphicsPathItem):
    def __init__(self, points: List[QPointF], pathway_id: Optional[int] = None):
        path = QPainterPath()
        if points:
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
        super().__init__(path)
        pen = QPen(QColor(160, 60, 200), 3)
        self.setPen(pen)
        self.setZValue(500)
        self.points = points
        self.pathway_id = pathway_id
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsMovable, False)

    def update_appearance(self, selected: bool = False):
        if selected:
            pen = QPen(QColor(255, 0, 0), 4)
        else:
            pen = QPen(QColor(160, 60, 200), 3)
        self.setPen(pen)


class StairItem(QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, stair_id: Optional[int] = None, to_floor_id: Optional[int] = None):
        size = 18.0
        rect = QRectF(x - size / 2, y - size / 2, size, size)
        super().__init__(rect)
        pen = QPen(QColor(30, 30, 30), 2)
        brush = QBrush(QColor(240, 220, 80, 200))
        self.setPen(pen)
        self.setBrush(brush)
        self.setZValue(1002)
        self.stair_id = stair_id
        self.to_floor_id = to_floor_id
        self.setToolTip(f"Stair to floor {to_floor_id}" if to_floor_id is not None else "Stair")


class FloorPlanCanvas(QGraphicsView):
    """Main canvas for displaying and editing floor plans."""

    # Signals
    room_selected = pyqtSignal(object)  # Emits RoomItem
    room_created = pyqtSignal(object)  # Emits RoomItem
    learning_status_changed = pyqtSignal(dict)  # Emits learning status dict
    stair_placement_requested = pyqtSignal(float, float)  # Emits x, y
    pathway_created = pyqtSignal(object)  # Emits PathwayItem
    pathway_deleted = pyqtSignal(int)  # Emits pathway_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Image background
        self.background_item = None
        self.current_image_path = None

        # Drawing state
        self.current_tool = "select"  # select, draw_room, draw_pathway, draw_stair
        self.drawing_points = []
        self.current_room_item = None
        self.suggestion_item = None
        self.auto_complete = AutoCompleteEngine()

        # Pattern learning
        self.pattern_learner = PatternLearner(demo_mode=False)
        self.pattern_suggestion_markers = []  # List of PatternSuggestionMarker items

        # Room items
        self.room_items = []
        self.selected_room = None

        # Navigation mode
        self.navigation_mode = False
        self.navigation_start_room = None
        self.navigation_end_room = None
        self.navigation_path_items = []  # Path visualization items
        self.last_navigation_path_by_floor = {}

        # Pathway and stair items
        self.pathway_items: List[PathwayItem] = []
        self.stair_items: List[StairItem] = []
        self.selected_pathway: Optional[PathwayItem] = None

        # Demo mode enhancements
        self.show_demo_help = True

        # View settings
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Mouse tracking
        self.setMouseTracking(True)

    def load_image(self, image_path: str):
        """Load and display floor plan image."""
        try:
            reader = QImageReader(image_path)
            reader.setAutoTransform(True)
            image = reader.read()
        except Exception:
            return False

        if image.isNull():
            return False

        # Downscale extremely large images to avoid GPU/OS crashes
        max_dimension = 8000
        if image.width() > max_dimension or image.height() > max_dimension:
            image = image.scaled(
                max_dimension,
                max_dimension,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        pixmap = QPixmap.fromImage(image)

        self.current_image_path = image_path

        # Remove old background if exists
        if self.background_item:
            self.scene.removeItem(self.background_item)

        # Add new background
        self.background_item = self.scene.addPixmap(pixmap)
        self.background_item.setZValue(-1)

        # Set scene rect to image size
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        # Fit image in view
        self.fitInView(self.background_item, Qt.AspectRatioMode.KeepAspectRatio)

        return True

    def set_tool(self, tool: str):
        """Set current drawing tool."""
        self.current_tool = tool
        self.cancel_drawing()

        if tool == "select":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

    def cancel_drawing(self):
        """Cancel current drawing operation."""
        self.drawing_points = []
        if self.current_room_item:
            self.scene.removeItem(self.current_room_item)
            self.current_room_item = None
        if self.suggestion_item:
            self.scene.removeItem(self.suggestion_item)
            self.suggestion_item = None

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.RightButton:
            if self.current_tool in ["draw_room", "draw_pathway"]:
                self.cancel_drawing()
                event.accept()
                return
        elif event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(pos, self.transform())

            if self.navigation_mode:
                if isinstance(item, RoomItem):
                    self.handle_navigation_click(item)
                    event.accept()
                    return

            if self.current_tool == "select":
                if isinstance(item, PatternSuggestionMarker):
                    x, y = item.suggestion_pos
                    size = item.room_half_size if getattr(item, "room_half_size", None) is not None else 50.0
                    vertices = [
                        [x - size, y - size],
                        [x + size, y - size],
                        [x + size, y + size],
                        [x - size, y + size],
                    ]
                    self.create_room_from_vertices(vertices)
                    event.accept()
                    return
                if isinstance(item, RoomItem):
                    self.deselect_pathway()
                    self.select_room(item)
                    event.accept()
                    return
                if isinstance(item, PathwayItem):
                    self.deselect_room()
                    self.select_pathway(item)
                    event.accept()
                    return
                self.deselect_room()
                self.deselect_pathway()

            elif self.current_tool in ["draw_room", "draw_pathway"]:
                self.drawing_points.append(pos)
                self.update_drawing_preview()
                event.accept()
                return

            elif self.current_tool == "draw_stair":
                self.stair_placement_requested.emit(pos.x(), pos.y())
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.current_tool in ["draw_room", "draw_pathway"] and self.drawing_points:
            scene_pos = self.mapToScene(event.pos())
            # Update preview with current mouse position
            self.update_drawing_preview(scene_pos)

        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to finish drawing."""
        if self.current_tool in ["draw_room", "draw_pathway"] and len(self.drawing_points) >= 2:
            self.finish_drawing()
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Accept suggestion
            if self.suggestion_item and self.drawing_points:
                self.accept_suggestion()
                event.accept()
                return
        elif event.key() == Qt.Key.Key_Escape:
            self.cancel_drawing()
            event.accept()
            return

        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if self.current_tool == "select" and self.selected_pathway is not None:
                self.delete_selected_pathway()
                event.accept()
                return

        super().keyPressEvent(event)

    def update_drawing_preview(self, current_pos: Optional[QPointF] = None):
        """Update drawing preview with current points and suggestions."""
        # Remove old preview
        if self.current_room_item:
            self.scene.removeItem(self.current_room_item)
            self.current_room_item = None
        if self.suggestion_item:
            self.scene.removeItem(self.suggestion_item)
            self.suggestion_item = None

        if not self.drawing_points:
            return

        preview_points = self.drawing_points.copy()
        if current_pos:
            preview_points.append(current_pos)

        if len(preview_points) < 2:
            return

        if self.current_tool == "draw_pathway":
            path = QPainterPath()
            path.moveTo(preview_points[0])
            for p in preview_points[1:]:
                path.lineTo(p)
            self.current_room_item = QGraphicsPathItem(path)
            pen = QPen(QColor(160, 60, 200), 2, Qt.PenStyle.DashLine)
            self.current_room_item.setPen(pen)
            self.current_room_item.setZValue(999)
            self.scene.addItem(self.current_room_item)
            return

        polygon = QPolygonF(preview_points)
        pen = QPen(QColor(0, 150, 255), 2, Qt.PenStyle.DashLine)
        brush = QBrush(QColor(0, 150, 255, 40))
        self.current_room_item = QGraphicsPolygonItem(polygon)
        self.current_room_item.setPen(pen)
        self.current_room_item.setBrush(brush)
        self.current_room_item.setZValue(999)
        self.scene.addItem(self.current_room_item)

        if len(self.drawing_points) >= 2:
            context = {
                "previous_rooms": self.room_items,
                "pattern_learner": self.pattern_learner,
                "scene_width": self.scene.width(),
                "scene_height": self.scene.height(),
            }
            suggestion = self.auto_complete.get_suggestion(
                self.drawing_points, self._get_autocomplete_tool(), context
            )
            if suggestion:
                if isinstance(suggestion, QRectF):
                    self.suggestion_item = SuggestionItem(suggestion)
                else:
                    self.suggestion_item = PolygonSuggestionItem(suggestion)
                if self.suggestion_item:
                    self.scene.addItem(self.suggestion_item)

    def accept_suggestion(self):
        """Accept the current suggestion and create room."""
        if self.current_tool != "draw_room":
            return
        if self.suggestion_item and len(self.drawing_points) >= 2:
            vertices = []
            if isinstance(self.suggestion_item, SuggestionItem):
                rect = self.suggestion_item.rect()
                vertices = [
                    [rect.left(), rect.top()],
                    [rect.right(), rect.top()],
                    [rect.right(), rect.bottom()],
                    [rect.left(), rect.bottom()]
                ]
            elif isinstance(self.suggestion_item, PolygonSuggestionItem):
                polygon = self.suggestion_item.polygon()
                vertices = [[point.x(), point.y()] for point in polygon]
            if vertices:
                self.create_room_from_vertices(vertices)
            self.cancel_drawing()

    def finish_drawing(self):
        """Finish drawing and create room from current points."""
        if len(self.drawing_points) < 2:
            return
        if self.current_tool == "draw_pathway":
            pathway = PathwayItem(self.drawing_points.copy())
            self.scene.addItem(pathway)
            self.pathway_items.append(pathway)
            self.pathway_created.emit(pathway)
            self.cancel_drawing()
            return
        vertices = [[p.x(), p.y()] for p in self.drawing_points]
        self.create_room_from_vertices(vertices)
        self.cancel_drawing()

    def create_room_from_vertices(self, vertices: List[List[float]]):
        """Create a room item from vertices."""
        room_item = RoomItem(vertices, name=f"Room {len(self.room_items) + 1}")
        self.scene.addItem(room_item)
        self.room_items.append(room_item)

        # Record pattern for learning
        # FIXED: Need 3 rooms minimum (room_{n-2}, room_{n-1}, room_n)
        # Note: room_items already includes the new room at this point
        if len(self.room_items) >= 3:
            # Get last 3 rooms: [room_{n-2}, room_{n-1}, room_n]
            room_sequence = [room.get_vertices() for room in self.room_items[-3:]]
            self.pattern_learner.record_pattern(room_sequence)

        # Update pattern suggestions
        self.update_pattern_suggestions()

        # Emit learning status update
        status = self.pattern_learner.get_status()
        self.learning_status_changed.emit(status)

        self.room_created.emit(room_item)

    def select_room(self, room_item: RoomItem):
        """Select a room item."""
        if self.selected_room:
            self.selected_room.update_appearance(selected=False)

        self.selected_room = room_item
        room_item.update_appearance(selected=True)
        self.room_selected.emit(room_item)

    def deselect_room(self):
        """Deselect current room."""
        if self.selected_room:
            self.selected_room.update_appearance(selected=False)
            self.selected_room = None
        self.room_selected.emit(None)

    def select_pathway(self, pathway_item: PathwayItem):
        if self.selected_pathway and self.selected_pathway is not pathway_item:
            self.selected_pathway.update_appearance(selected=False)
        self.selected_pathway = pathway_item
        pathway_item.update_appearance(selected=True)

    def deselect_pathway(self):
        if self.selected_pathway:
            self.selected_pathway.update_appearance(selected=False)
            self.selected_pathway = None

    def delete_selected_pathway(self):
        item = self.selected_pathway
        if item is None:
            return
        pathway_id = item.pathway_id
        if item in self.pathway_items:
            self.pathway_items.remove(item)
        self.scene.removeItem(item)
        self.selected_pathway = None
        if pathway_id is not None:
            self.pathway_deleted.emit(int(pathway_id))

    def add_room_item(self, room_item: RoomItem):
        """Add a room item to the canvas (e.g., from database)."""
        self.scene.addItem(room_item)
        self.room_items.append(room_item)

    def remove_room_item(self, room_item: RoomItem):
        """Remove a room item from the canvas."""
        if room_item in self.room_items:
            self.scene.removeItem(room_item)
            self.room_items.remove(room_item)
        if self.selected_room == room_item:
            self.selected_room = None
            self.room_selected.emit(None)
        # Update suggestions after removal
        self.update_pattern_suggestions()

    def clear_rooms(self):
        """Clear all room items."""
        for item in self.room_items:
            self.scene.removeItem(item)
        self.room_items.clear()
        self.selected_room = None
        self.clear_pattern_suggestions()
        self.clear_navigation_path()  # Also clear navigation paths
        self.clear_pathways()
        self.clear_stairs()

    def clear_pathways(self):
        self.deselect_pathway()
        for item in self.pathway_items:
            self.scene.removeItem(item)
        self.pathway_items.clear()

    def add_pathway_item(self, points: List[Tuple[float, float]], pathway_id: Optional[int] = None):
        qpoints = [QPointF(float(x), float(y)) for x, y in points]
        item = PathwayItem(qpoints, pathway_id=pathway_id)
        self.scene.addItem(item)
        self.pathway_items.append(item)
        return item

    def clear_stairs(self):
        for item in self.stair_items:
            self.scene.removeItem(item)
        self.stair_items.clear()

    def add_stair_item(self, x: float, y: float, stair_id: Optional[int] = None, to_floor_id: Optional[int] = None):
        item = StairItem(x, y, stair_id=stair_id, to_floor_id=to_floor_id)
        self.scene.addItem(item)
        self.stair_items.append(item)

    def clear_pattern_suggestions(self):
        """Clear pattern suggestion markers."""
        for marker in self.pattern_suggestion_markers:
            self.scene.removeItem(marker)
        self.pattern_suggestion_markers.clear()

    
    def set_navigation_mode(self, enabled: bool):
        """Enable or disable navigation mode."""
        self.navigation_mode = enabled
        
        if enabled:
            # Clear existing navigation state
            self.clear_navigation_path()
            self.navigation_start_room = None
            self.navigation_end_room = None
            print("[DEMO] Navigation mode enabled")
        else:
            # Clear navigation visualization
            self.clear_navigation_path()
            print("[DEMO] Navigation mode disabled")
    
    def clear_navigation_path(self):
        """Clear navigation path visualization."""
        for item in self.navigation_path_items:
            self.scene.removeItem(item)
        self.navigation_path_items.clear()
    
    def handle_navigation_click(self, room_item: RoomItem):
        """Handle room click in navigation mode."""
        if not self.navigation_mode:
            return
        
        if self.navigation_start_room is None:
            # Set start room
            self.navigation_start_room = room_item
            room_item.update_appearance(selected=True, is_navigation_start=True)
            print(f"[DEMO] Navigation start: {room_item.name}")
        elif self.navigation_end_room is None and room_item != self.navigation_start_room:
            # Set end room and calculate path
            self.navigation_end_room = room_item
            room_item.update_appearance(selected=True, is_navigation_end=True)
            print(f"[DEMO] Navigation end: {room_item.name}")
            
            # Calculate and display path
            self.calculate_and_display_path()
        else:
            # Reset and start new navigation
            self.clear_navigation_path()
            if self.navigation_start_room:
                self.navigation_start_room.update_appearance(selected=False)
            if self.navigation_end_room:
                self.navigation_end_room.update_appearance(selected=False)
            
            self.navigation_start_room = room_item
            self.navigation_end_room = None
            room_item.update_appearance(selected=True, is_navigation_start=True)
            print(f"[DEMO] New navigation start: {room_item.name}")
    
    def calculate_and_display_path(self):
        """Calculate path between selected rooms and display it."""
        if not self.navigation_start_room or not self.navigation_end_room:
            return
        
        # Use navigation controller to calculate path
        try:
            # Set start and end rooms in navigation controller
            if hasattr(self.parent(), 'navigation_controller'):
                nav_controller = self.parent().navigation_controller
                nav_controller.set_start_room(self.navigation_start_room.room_id)
                nav_controller.set_end_room(self.navigation_end_room.room_id)
                
                # Get path by floor
                path_by_floor = nav_controller.get_path_by_floor()

                current_floor_id = None
                if hasattr(self.parent(), "current_floor_id"):
                    current_floor_id = getattr(self.parent(), "current_floor_id")

                # Display path
                self.display_navigation_path(path_by_floor, current_floor_id=current_floor_id)
                
                print(f"[DEMO] Path calculated across {len(path_by_floor)} floor(s)")
                
        except Exception as e:
            print(f"[DEMO] Error calculating path: {e}")
    
    def display_navigation_path(self, path_by_floor: dict, current_floor_id: Optional[int] = None):
        """Display navigation path visualization (only for the current floor)."""
        self.last_navigation_path_by_floor = path_by_floor or {}
        self.clear_navigation_path()

        if current_floor_id is None:
            return

        points = self.last_navigation_path_by_floor.get(current_floor_id, [])
        if len(points) < 2:
            return

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            line = self.scene.addLine(x1, y1, x2, y2)
            line.setPen(QPen(QColor(255, 0, 0), 3))
            line.setZValue(999)
            self.navigation_path_items.append(line)

            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            arrow = self.scene.addEllipse(mid_x - 3, mid_y - 3, 6, 6)
            arrow.setBrush(QBrush(QColor(255, 0, 0)))
            arrow.setPen(QPen(QColor(255, 0, 0), 2))
            arrow.setZValue(1000)
            self.navigation_path_items.append(arrow)
    
    def update_pattern_suggestions(self):
        """Update pattern-based room position suggestions with enhanced markers."""
        # Clear existing markers
        self.clear_pattern_suggestions()
        
        # Show suggestions if we have at least 1 room
        # (suggestions will work with 1+ rooms, but are best with 2+)
        if len(self.room_items) < 1:
            return
        
        # Get recent rooms for pattern matching (use last 2 if available)
        recent_rooms = [room.get_vertices() for room in self.room_items[-2:]]
        
        # Get suggestions with room types and confidence
        suggestions = self.pattern_learner.suggest_positions(recent_rooms, num_suggestions=3)
        
        # Create enhanced markers for suggestions
        for suggestion in suggestions:
            if len(suggestion) >= 5:  # (x, y, room_type, confidence, suggested_area)
                x, y, room_type, confidence, suggested_area = suggestion
                marker = PatternSuggestionMarker(
                    x,
                    y,
                    room_type=room_type,
                    confidence=confidence,
                    suggested_area=suggested_area,
                )
                self.scene.addItem(marker)
                self.pattern_suggestion_markers.append(marker)
            elif len(suggestion) >= 4:  # (x, y, room_type, confidence)
                x, y, room_type, confidence = suggestion
                marker = PatternSuggestionMarker(x, y, room_type=room_type, confidence=confidence)
                self.scene.addItem(marker)
                self.pattern_suggestion_markers.append(marker)
            elif len(suggestion) >= 2:  # Backward compatibility with (x, y) tuples
                x, y = suggestion
                marker = PatternSuggestionMarker(x, y, room_type="Room", confidence=0.7)
                self.scene.addItem(marker)
                self.pattern_suggestion_markers.append(marker)
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        # Zoom with Ctrl+Wheel
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            scale_factor = 1.15
            if event.angleDelta().y() < 0:
                scale_factor = 1.0 / scale_factor
            self.scale(scale_factor, scale_factor)
        else:
            super().wheelEvent(event)

    def _get_autocomplete_tool(self) -> str:
        """Map current tool to auto-complete tool type."""
        if self.current_tool == "draw_room":
            return "room"
        return self.current_tool

