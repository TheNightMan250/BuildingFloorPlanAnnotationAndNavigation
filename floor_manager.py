"""
Floor management panel for handling multiple floors.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QInputDialog, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from models import FloorPlan, Room


class FloorManager(QWidget):
    """Dockable panel for managing multiple floor plans."""
    
    # Signals
    floor_selected = pyqtSignal(int)  # Emits floor_plan_id
    floor_added = pyqtSignal(str, str)  # Emits name, image_path
    floor_deleted = pyqtSignal(int)  # Emits floor_plan_id
    
    def __init__(self, db_session=None, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self.current_floor_id = None
        self.init_ui()
        self.refresh_floors()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Floors")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Floor list
        self.floor_list = QListWidget()
        self.floor_list.itemClicked.connect(self.on_floor_selected)
        layout.addWidget(self.floor_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Floor")
        self.add_button.clicked.connect(self.on_add_floor)
        button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete_floor)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def set_db_session(self, session):
        """Set database session."""
        self.db_session = session
        self.refresh_floors()
    
    def refresh_floors(self):
        """Refresh the floor list from database."""
        self.floor_list.clear()
        
        if not self.db_session:
            return
        
        try:
            floors = self.db_session.query(FloorPlan).all()
            for floor in floors:
                item_text = f"{floor.name} (ID: {floor.id})"
                self.floor_list.addItem(item_text)
                # Store floor_id in item data
                item = self.floor_list.item(self.floor_list.count() - 1)
                item.setData(256, floor.id)  # Qt.ItemDataRole.UserRole = 256
            
            if floors:
                self.info_label.setText(f"Total floors: {len(floors)}")
            else:
                self.info_label.setText("No floors. Add a floor to get started.")
        except Exception as e:
            self.info_label.setText(f"Error loading floors: {str(e)}")
    
    def on_floor_selected(self, item):
        """Handle floor selection."""
        floor_id = item.data(256)  # Qt.ItemDataRole.UserRole
        if floor_id:
            self.current_floor_id = floor_id
            self.floor_selected.emit(floor_id)
    
    def on_add_floor(self):
        """Handle add floor button."""
        name, ok = QInputDialog.getText(self, "Add Floor", "Floor Name:")
        if ok and name:
            # Emit signal - parent will handle file dialog and database
            self.floor_added.emit(name, "")
    
    def on_delete_floor(self):
        """Handle delete floor button."""
        current_item = self.floor_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a floor to delete.")
            return
        
        floor_id = current_item.data(256)
        if not floor_id:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Floor", 
            f"Are you sure you want to delete this floor?\nThis will also delete all rooms on this floor.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.floor_deleted.emit(floor_id)
            self.refresh_floors()
    
    def set_current_floor(self, floor_id: int):
        """Set the currently selected floor."""
        self.current_floor_id = floor_id
        # Highlight in list
        for i in range(self.floor_list.count()):
            item = self.floor_list.item(i)
            if item.data(256) == floor_id:
                self.floor_list.setCurrentItem(item)
                break

