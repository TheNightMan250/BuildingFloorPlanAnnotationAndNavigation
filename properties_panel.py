"""
Properties panel for editing room and floor plan properties.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import pyqtSignal
from canvas_widget import RoomItem


class PropertiesPanel(QWidget):
    """Dockable panel for editing selected item properties."""
    
    # Signals
    room_updated = pyqtSignal(object)  # Emits RoomItem
    room_deleted = pyqtSignal(object)  # Emits RoomItem
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_room = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Room properties group
        room_group = QGroupBox("Room Properties")
        room_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Room Name")
        self.name_edit.textChanged.connect(self.on_property_changed)
        room_layout.addRow("Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Room", "Bedroom", "Bathroom", "Kitchen", 
                                  "Living Room", "Hallway", "Office", "Other"])
        self.type_combo.currentTextChanged.connect(self.on_property_changed)
        room_layout.addRow("Type:", self.type_combo)
        
        self.delete_button = QPushButton("Delete Room")
        self.delete_button.setStyleSheet("background-color: #dc3545; color: white;")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        room_layout.addRow(self.delete_button)
        
        room_group.setLayout(room_layout)
        layout.addWidget(room_group)
        
        # Info label
        self.info_label = QLabel("Select a room to edit properties")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Learning status group
        learning_group = QGroupBox("Pattern Learning Status")
        learning_layout = QFormLayout()
        
        self.patterns_label = QLabel("0")
        learning_layout.addRow("Patterns Collected:", self.patterns_label)
        
        self.model_status_label = QLabel("Not Trained")
        learning_layout.addRow("Model Status:", self.model_status_label)
        
        self.performance_label = QLabel("")
        self.performance_label.setWordWrap(True)
        learning_layout.addRow("Performance:", self.performance_label)
        
        learning_group.setLayout(learning_layout)
        layout.addWidget(learning_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Initially disable editing
        self.set_enabled(False)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable property editing."""
        self.name_edit.setEnabled(enabled)
        self.type_combo.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
    
    def set_room(self, room_item: RoomItem):
        """Set the room to edit."""
        self.current_room = room_item
        
        if room_item:
            self.name_edit.setText(room_item.name)
            index = self.type_combo.findText(room_item.room_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            self.info_label.setText(f"Editing: {room_item.name}")
            self.set_enabled(True)
        else:
            self.name_edit.clear()
            self.type_combo.setCurrentIndex(0)
            self.info_label.setText("Select a room to edit properties")
            self.set_enabled(False)
    
    def on_property_changed(self):
        """Handle property change."""
        if self.current_room:
            self.current_room.name = self.name_edit.text()
            self.current_room.room_type = self.type_combo.currentText()
            self.room_updated.emit(self.current_room)
    
    def on_delete_clicked(self):
        """Handle delete button click."""
        if self.current_room:
            self.room_deleted.emit(self.current_room)
            self.set_room(None)
    
    def update_learning_status(self, status: dict):
        """Update learning status display with performance metrics."""
        self.patterns_label.setText(str(status.get("patterns_collected", 0)))
        if status.get("model_trained", False):
            self.model_status_label.setText("Trained")
            self.model_status_label.setStyleSheet("color: green;")
            
            # Show performance metrics (only if reliable)
            if status.get("distance_r2") is not None:
                dist_r2 = status.get("distance_r2", 0)
                dir_r2 = status.get("direction_r2", 0)
                dist_rmse = status.get("distance_rmse", 0)
                samples = status.get("training_samples", 0)
                test_samples = status.get("test_samples", 0)
                
                perf_text = f"R²: Dist={dist_r2:.2f}, Dir={dir_r2:.2f}\n"
                perf_text += f"RMSE: Dist={dist_rmse:.1f}\n"
                perf_text += f"Train: {samples}, Test: {test_samples}"
                self.performance_label.setText(perf_text)
            else:
                # Insufficient data for reliable metrics
                samples = status.get("training_samples", 0)
                note = status.get("metrics_note", "")
                perf_text = f"Training samples: {samples}\n"
                perf_text += f"{note}"
                self.performance_label.setText(perf_text)
        else:
            self.model_status_label.setText("Not Trained")
            self.model_status_label.setStyleSheet("color: orange;")
            self.performance_label.setText("Need 5+ patterns to train")

