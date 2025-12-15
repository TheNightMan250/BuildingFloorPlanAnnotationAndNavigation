from PyQt6.QtWidgets import (QMainWindow, QMenuBar, QToolBar, QStatusBar, 
                              QDockWidget, QFileDialog, QMessageBox, QInputDialog,
                              QWidget, QVBoxLayout, QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from canvas_widget import FloorPlanCanvas, RoomItem
from properties_panel import PropertiesPanel
from floor_manager import FloorManager
from domain.buildings.room import Room as DomainRoom
from domain.buildings.floor import Floor as DomainFloor
from domain.buildings.stair import Stair
from data.repositories.stair_repo import StairRepository
from domain.buildings.pathway import Pathway
from data.repositories.pathway_repo import PathwayRepository
from typing import Optional
import os


def get_icon_path(icon_name: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(os.path.dirname(base_dir), "assets", "icons")
    formats = [".png", ".svg", ".ico", ".jpg", ".jpeg"]
    for fmt in formats:
        icon_path = os.path.join(icons_dir, f"{icon_name}{fmt}")
        if os.path.exists(icon_path):
            return icon_path
    return ""


def load_icon(icon_name: str) -> QIcon:
    icon_path = get_icon_path(icon_name)
    if icon_path:
        return QIcon(icon_path)
    return QIcon()


class MainWindow(QMainWindow):
    def __init__(self, ui, map_controller, navigation_controller, room_repo, db_session, db_engine=None):
        super().__init__()
        self.ui = ui
        self.map_controller = map_controller
        self.navigation_controller = navigation_controller
        self.room_repo = room_repo
        self.db_session = db_session
        self.db_engine = db_engine
        self.current_floor_id: Optional[int] = None
        self.navigation_mode = False
        self.nav_start_room_id: Optional[int] = None
        self.nav_end_room_id: Optional[int] = None
        
        self.init_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_docks()
        self.setup_connections()
        
        self.setWindowTitle("Floor Plan Drawing App")
        self.resize(1200, 800)
    
    def init_ui(self):
        self.canvas = FloorPlanCanvas(self)
        self.setCentralWidget(self.canvas)
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        open_image_action = QAction(load_icon("open"), "&Open Image...", self)
        open_image_action.setShortcut(QKeySequence("Ctrl+O"))
        open_image_action.triggered.connect(self.open_image)
        file_menu.addAction(open_image_action)
        
        new_floor_action = QAction(load_icon("new_floor"), "&New Floor...", self)
        new_floor_action.setShortcut(QKeySequence("Ctrl+N"))
        new_floor_action.triggered.connect(self.new_floor)
        file_menu.addAction(new_floor_action)
        
        file_menu.addSeparator()
        
        save_action = QAction(load_icon("save"), "&Save Project", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        load_action = QAction(load_icon("load"), "&Load Project...", self)
        load_action.setShortcut(QKeySequence("Ctrl+L"))
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        tools_menu = menubar.addMenu("&Tools")
        select_action = QAction("&Select", self)
        select_action.setShortcut(QKeySequence("S"))
        select_action.setCheckable(True)
        select_action.setChecked(True)
        select_action.triggered.connect(lambda: self.set_tool("select"))
        tools_menu.addAction(select_action)
        
        draw_room_action = QAction("Draw &Room", self)
        draw_room_action.setShortcut(QKeySequence("R"))
        draw_room_action.setCheckable(True)
        draw_room_action.triggered.connect(lambda: self.set_tool("draw_room"))
        tools_menu.addAction(draw_room_action)
        
        draw_pathway_action = QAction("Draw &Pathway", self)
        draw_pathway_action.setShortcut(QKeySequence("P"))
        draw_pathway_action.setCheckable(True)
        draw_pathway_action.triggered.connect(lambda: self.set_tool("draw_pathway"))
        tools_menu.addAction(draw_pathway_action)
        
        draw_stair_action = QAction("Draw &Stair", self)
        draw_stair_action.setShortcut(QKeySequence("T"))
        draw_stair_action.setCheckable(True)
        draw_stair_action.triggered.connect(lambda: self.set_tool("draw_stair"))
        tools_menu.addAction(draw_stair_action)
        
        view_menu = menubar.addMenu("&View")
        zoom_in_action = QAction(load_icon("zoom_in"), "Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl++"))
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction(load_icon("zoom_out"), "Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_action = QAction(load_icon("fit_window"), "&Fit to Window", self)
        fit_action.setShortcut(QKeySequence("Ctrl+0"))
        fit_action.triggered.connect(self.fit_to_window)
        view_menu.addAction(fit_action)
        
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        select_action = QAction(load_icon("select"), "Select", self)
        select_action.setCheckable(True)
        select_action.setChecked(True)
        select_action.triggered.connect(lambda: self.set_tool("select"))
        toolbar.addAction(select_action)
        
        toolbar.addSeparator()
        
        draw_room_action = QAction(load_icon("draw_room"), "Draw Room", self)
        draw_room_action.setCheckable(True)
        draw_room_action.triggered.connect(lambda: self.set_tool("draw_room"))
        toolbar.addAction(draw_room_action)
        
        draw_pathway_action = QAction(load_icon("draw_pathway"), "Draw Pathway", self)
        draw_pathway_action.setCheckable(True)
        draw_pathway_action.triggered.connect(lambda: self.set_tool("draw_pathway"))
        toolbar.addAction(draw_pathway_action)
        
        draw_stair_action = QAction(load_icon("new_floor"), "Draw Stair", self)
        draw_stair_action.setCheckable(True)
        draw_stair_action.triggered.connect(lambda: self.set_tool("draw_stair"))
        toolbar.addAction(draw_stair_action)
        
        toolbar.addSeparator()
        
        # Navigation mode
        navigation_action = QAction(load_icon("select"), "Navigation Mode", self)
        navigation_action.setCheckable(True)
        navigation_action.triggered.connect(self.toggle_navigation_mode)
        toolbar.addAction(navigation_action)
        
        self.tool_actions = [select_action, draw_room_action, draw_pathway_action, draw_stair_action]
    
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def setup_docks(self):
        properties_dock = QDockWidget("Properties", self)
        self.properties_panel = PropertiesPanel(self)
        properties_dock.setWidget(self.properties_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, properties_dock)
        
        floor_dock = QDockWidget("Floors", self)
        self.floor_manager = FloorManager(self.db_session, self)
        floor_dock.setWidget(self.floor_manager)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, floor_dock)

        self.navigation_dock = QDockWidget("Navigation", self)
        self.navigation_panel = QWidget(self)
        nav_layout = QVBoxLayout(self.navigation_panel)

        self.nav_status_label = QLabel("Select a start room", self.navigation_panel)
        nav_layout.addWidget(self.nav_status_label)

        self.nav_search = QLineEdit(self.navigation_panel)
        self.nav_search.setPlaceholderText("Search rooms...")
        nav_layout.addWidget(self.nav_search)

        self.nav_tree = QTreeWidget(self.navigation_panel)
        self.nav_tree.setHeaderHidden(True)
        nav_layout.addWidget(self.nav_tree)

        self.navigation_dock.setWidget(self.navigation_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.navigation_dock)
        self.navigation_dock.hide()
    
    def setup_connections(self):
        self.canvas.room_selected.connect(self.on_room_selected)
        self.canvas.room_created.connect(self.on_room_created)
        self.canvas.learning_status_changed.connect(self.on_learning_status_changed)
        self.canvas.stair_placement_requested.connect(self.on_stair_placement_requested)
        self.canvas.pathway_created.connect(self.on_pathway_created)
        self.canvas.pathway_deleted.connect(self.on_pathway_deleted)
        
        self.properties_panel.room_updated.connect(self.on_room_updated)
        self.properties_panel.room_deleted.connect(self.on_room_deleted)
        
        self.floor_manager.floor_selected.connect(self.on_floor_selected)
        self.floor_manager.floor_added.connect(self.on_floor_added)
        self.floor_manager.floor_deleted.connect(self.on_floor_deleted)

        self.nav_search.textChanged.connect(self.on_nav_search_changed)
        self.nav_tree.itemDoubleClicked.connect(self.on_nav_tree_item_double_clicked)
        
        self.update_learning_status()
    
    def toggle_navigation_mode(self):
        """Toggle between annotation and navigation modes."""
        self.navigation_mode = not self.navigation_mode
        
        if self.navigation_mode:
            # Enter navigation mode
            self.canvas.set_navigation_mode(True)
            self.navigation_controller.clear_selection()
            self.nav_start_room_id = None
            self.nav_end_room_id = None
            self.nav_status_label.setText("Select a start room")
            self.refresh_navigation_room_list()
            self.navigation_dock.show()
            self.status_bar.showMessage("Navigation Mode: Select start room")
            print("[DEMO] Navigation Mode Activated")
        else:
            # Exit navigation mode
            self.canvas.set_navigation_mode(False)
            self.navigation_controller.clear_selection()
            self.nav_start_room_id = None
            self.nav_end_room_id = None
            self.navigation_dock.hide()
            self.status_bar.showMessage("Annotation Mode")
            print("[DEMO] Navigation Mode Deactivated")
    
    def set_tool(self, tool_name: str):
        """Set the current drawing tool."""
        # Disable navigation mode when switching tools
        if self.navigation_mode:
            self.toggle_navigation_mode()
        
        # Uncheck all tool actions
        for action in self.tool_actions:
            action.setChecked(False)
        
        # Check the selected tool action
        tool_map = {
            "select": 0,
            "draw_room": 1,
            "draw_pathway": 2,
            "draw_stair": 3,
        }
        if tool_name in tool_map:
            self.tool_actions[tool_map[tool_name]].setChecked(True)
        
        self.canvas.set_tool(tool_name)
        self.status_bar.showMessage(f"Tool: {tool_name.replace('_', ' ').title()}")

    def on_stair_placement_requested(self, x: float, y: float):
        if not self.current_floor_id:
            QMessageBox.warning(self, "Stairs", "Select a floor first.")
            return

        floors = self.map_controller.map_repo.find_all()
        floor_choices = [
            f"{f.floor_id}: {f.name}"
            for f in floors
            if f.floor_id and f.floor_id != self.current_floor_id
        ]
        if not floor_choices:
            QMessageBox.information(self, "Stairs", "No other floors exist. Add another floor first.")
            return

        choice, ok = QInputDialog.getItem(
            self,
            "Connect Stair",
            "Connect this stair to which floor?",
            floor_choices,
            0,
            False,
        )
        if not ok or not choice:
            return

        try:
            to_floor_id = int(choice.split(":", 1)[0])
        except Exception:
            QMessageBox.warning(self, "Stairs", "Invalid floor selection.")
            return

        stair_repo = StairRepository(self.db_session, self.db_engine)
        stair = Stair(None, self.current_floor_id, to_floor_id, (float(x), float(y)))
        stair = stair_repo.save(stair)

        self.canvas.add_stair_item(float(x), float(y), stair_id=stair.stair_id, to_floor_id=to_floor_id)
        self.status_bar.showMessage(f"Placed stair to floor {to_floor_id}")
    
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Floor Plan Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_path:
            if self.canvas.load_image(file_path):
                self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load image file.")
    
    def new_floor(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Floor Plan Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if not file_path:
            return
        
        name, ok = QFileDialog.getSaveFileName(
            self, "Save Floor Plan", "",
            "Floor Plan Files (*.db);;All Files (*)"
        )
        if not ok:
            return
        
        floor = DomainFloor(None, os.path.basename(name), file_path)
        saved_floor = self.map_controller.submit_map(floor)
        
        if saved_floor:
            self.current_floor_id = saved_floor.floor_id
            self.canvas.load_image(file_path)
            self.floor_manager.refresh_floors()
            self.floor_manager.set_current_floor(saved_floor.floor_id)
            self.status_bar.showMessage(f"Created floor: {saved_floor.name}")
    
    def on_floor_selected(self, floor_id: int):
        floor = self.map_controller.load_map(floor_id)
        if floor:
            self.current_floor_id = floor_id
            self.canvas.load_image(floor.image_path)
            self.load_rooms_for_floor(floor_id)
            self.load_stairs_for_floor(floor_id)
            self.load_pathways_for_floor(floor_id)
            if self.navigation_mode:
                self.canvas.display_navigation_path(self.canvas.last_navigation_path_by_floor, current_floor_id=floor_id)
            self.status_bar.showMessage(f"Loaded floor: {floor.name}")

    def load_pathways_for_floor(self, floor_id: int):
        pathway_repo = PathwayRepository(self.db_session, self.db_engine)
        pathways = pathway_repo.find_by_floor(floor_id)
        self.canvas.clear_pathways()
        for p in pathways:
            self.canvas.add_pathway_item(p.points, pathway_id=p.pathway_id)

    def load_stairs_for_floor(self, floor_id: int):
        stair_repo = StairRepository(self.db_session, self.db_engine)
        stairs = stair_repo.find_by_floor(floor_id)
        # Clear and re-add (stairs are per-floor view)
        self.canvas.clear_stairs()
        for stair in stairs:
            x, y = stair.position
            to_floor_id = stair.get_other_floor(floor_id)
            self.canvas.add_stair_item(float(x), float(y), stair_id=stair.stair_id, to_floor_id=to_floor_id)
    
    def on_floor_added(self, name: str, image_path: str):
        if not image_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Floor Plan Image", "",
                "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
            )
            if not file_path:
                return
            image_path = file_path
        
        floor = DomainFloor(None, name, image_path)
        saved_floor = self.map_controller.submit_map(floor)
        if saved_floor:
            self.floor_manager.refresh_floors()
            self.on_floor_selected(saved_floor.floor_id)
    
    def on_floor_deleted(self, floor_id: int):
        floor = self.map_controller.map_repo.find_by_id(floor_id)
        if floor and self.map_controller.map_repo.delete(floor_id):
            if self.current_floor_id == floor_id:
                self.current_floor_id = None
                self.canvas.clear_rooms()
                if self.canvas.background_item:
                    self.canvas.scene.removeItem(self.canvas.background_item)
                    self.canvas.background_item = None
            self.floor_manager.refresh_floors()
            self.status_bar.showMessage(f"Deleted floor: {floor_id}")
    
    def on_room_selected(self, room_item: RoomItem):
        self.properties_panel.set_room(room_item)
    
    def on_room_created(self, room_item: RoomItem):
        if self.current_floor_id:
            domain_room = DomainRoom(
                None,
                room_item.name,
                room_item.room_type,
                room_item.get_vertices(),
                self.current_floor_id
            )
            saved_room = self.map_controller.create_room(
                self.current_floor_id,
                room_item.name,
                room_item.room_type,
                room_item.get_vertices()
            )
            room_item.room_id = saved_room.room_id
            self.status_bar.showMessage(f"Created room: {room_item.name}")
    
    def on_room_updated(self, room_item: RoomItem):
        if room_item.room_id:
            domain_room = DomainRoom(
                room_item.room_id,
                room_item.name,
                room_item.room_type,
                room_item.get_vertices(),
                self.current_floor_id or 0
            )
            self.room_repo.save(domain_room)
            self.status_bar.showMessage(f"Updated room: {room_item.name}")
        else:
            self.on_room_created(room_item)
    
    def on_room_deleted(self, room_item: RoomItem):
        if not room_item:
            return
        if room_item.room_id:
            self.map_controller.delete_room(room_item.room_id)
        self.canvas.remove_room_item(room_item)
        self.status_bar.showMessage(f"Deleted room: {room_item.name}")
        self.update_learning_status()
    
    def on_learning_status_changed(self, status: dict):
        self.properties_panel.update_learning_status(status)
    
    def update_learning_status(self):
        status = self.canvas.pattern_learner.get_status()
        self.properties_panel.update_learning_status(status)
    
    def load_rooms_for_floor(self, floor_id: int):
        self.canvas.clear_rooms()
        rooms = self.room_repo.find_by_floor_id(floor_id)
        for room in rooms:
            room_item = RoomItem(
                room.vertices,
                room_id=room.room_id,
                name=room.name,
                room_type=room.room_type
            )
            self.canvas.add_room_item(room_item)
        self.canvas.update_pattern_suggestions()
        self.update_learning_status()

    def on_pathway_created(self, pathway_item):
        if not self.current_floor_id:
            return

        points = [(float(p.x()), float(p.y())) for p in getattr(pathway_item, "points", [])]
        if len(points) < 2:
            return

        pathway_repo = PathwayRepository(self.db_session, self.db_engine)
        saved = pathway_repo.save(Pathway(None, self.current_floor_id, points))
        pathway_item.pathway_id = saved.pathway_id

    def on_pathway_deleted(self, pathway_id: int):
        pathway_repo = PathwayRepository(self.db_session, self.db_engine)
        pathway_repo.delete(int(pathway_id))

    def refresh_navigation_room_list(self):
        self.nav_tree.clear()
        floors = self.map_controller.map_repo.find_all()
        for floor in floors:
            if not floor.floor_id:
                continue
            top = QTreeWidgetItem([f"{floor.name} (ID: {floor.floor_id})"])
            top.setData(0, 256, ("floor", floor.floor_id))
            self.nav_tree.addTopLevelItem(top)
            rooms = self.room_repo.find_by_floor_id(floor.floor_id)
            rooms_sorted = sorted(rooms, key=lambda r: (r.name or ""))
            for room in rooms_sorted:
                child = QTreeWidgetItem([f"{room.name} ({room.room_type})"])
                child.setData(0, 256, ("room", room.room_id, floor.floor_id))
                top.addChild(child)
            top.setExpanded(True)

        self.on_nav_search_changed(self.nav_search.text())

    def on_nav_search_changed(self, text: str):
        query = (text or "").strip().lower()
        for i in range(self.nav_tree.topLevelItemCount()):
            floor_item = self.nav_tree.topLevelItem(i)
            any_visible = False
            for j in range(floor_item.childCount()):
                child = floor_item.child(j)
                label = (child.text(0) or "").lower()
                visible = (query == "") or (query in label)
                child.setHidden(not visible)
                any_visible = any_visible or visible
            floor_item.setHidden(not any_visible)

    def on_nav_tree_item_double_clicked(self, item, column: int):
        data = item.data(0, 256)
        if not data or data[0] != "room":
            return
        _, room_id, floor_id = data
        room_id = int(room_id)
        floor_id = int(floor_id)

        if self.nav_start_room_id is None or (self.nav_start_room_id is not None and self.nav_end_room_id is not None):
            self.nav_start_room_id = room_id
            self.nav_end_room_id = None
            self.nav_status_label.setText("Select an end room")
        else:
            self.nav_end_room_id = room_id
            self.nav_status_label.setText("Route ready")

        if self.current_floor_id != floor_id:
            self.on_floor_selected(floor_id)

        if self.nav_start_room_id is not None:
            self.navigation_controller.set_start_room(self.nav_start_room_id)
        if self.nav_end_room_id is not None:
            self.navigation_controller.set_end_room(self.nav_end_room_id)

        if self.nav_start_room_id is not None and self.nav_end_room_id is not None:
            path_by_floor = self.navigation_controller.get_path_by_floor()
            self.canvas.display_navigation_path(path_by_floor, current_floor_id=self.current_floor_id)
    
    def save_project(self):
        self.status_bar.showMessage("Project saved")
        QMessageBox.information(self, "Save", "Project saved successfully!")
    
    def load_project(self):
        self.floor_manager.refresh_floors()
        self.status_bar.showMessage("Project loaded")
    
    def zoom_in(self):
        self.canvas.scale(1.2, 1.2)
    
    def zoom_out(self):
        self.canvas.scale(1.0 / 1.2, 1.0 / 1.2)
    
    def fit_to_window(self):
        if self.canvas.background_item:
            self.canvas.fitInView(self.canvas.background_item, Qt.AspectRatioMode.KeepAspectRatio)
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About Floor Plan Drawing App",
            "Floor Plan Drawing App with Smart Auto-Completion\n\nVersion 1.0\n\n"
            "A PyQt6 application for marking floor plans with intelligent drawing assistance."
        )
    
    def closeEvent(self, event):
        try:
            if hasattr(self, "canvas") and hasattr(self.canvas, "pattern_learner"):
                learner = self.canvas.pattern_learner
                if getattr(learner, "demo_mode", False) is False and getattr(learner, "patterns", None) is not None:
                    if len(learner.patterns) >= 5:
                        learner.train_model()
        except Exception:
            pass

        self.db_session.close()
        event.accept()

