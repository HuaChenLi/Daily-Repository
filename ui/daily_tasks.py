from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                             QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime

class DailyTasksTab(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.task_checkboxes = {}  # goal_id -> checkbox mapping
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Header with today's date
        header = QLabel(f"Tasks for {self.today}")
        header_font = QFont("Segoe UI", 12, QFont.Bold)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Scroll area for tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.tasks_layout = scroll_layout
        self.tasks_container = scroll_widget
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        self.refresh()
    
    def refresh(self):
        """Refresh the task list"""
        # Clear existing checkboxes
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        self.task_checkboxes.clear()
        
        # Get all goals grouped by category
        categories = self.db.get_categories()
        
        if not categories:
            label = QLabel("No categories yet. Add one in 'Manage Goals' tab.")
            self.tasks_layout.addWidget(label)
            return
        
        # Display tasks by category
        for cat_id, cat_name, cat_color in categories:
            goals = self.db.get_goals_by_category(cat_id)
            
            if goals:
                # Category group box
                group = QGroupBox(cat_name)
                group.setFont(QFont("Segoe UI", 10))
                group_layout = QVBoxLayout()
                
                # Tasks in category
                for goal_id, goal_name in goals:
                    is_completed = self.db.is_goal_completed(goal_id, self.today)
                    
                    checkbox = QCheckBox(goal_name)
                    checkbox.setFont(QFont("Segoe UI", 9))
                    checkbox.setChecked(is_completed)
                    checkbox.stateChanged.connect(lambda state, gid=goal_id: self.on_task_toggle(gid))
                    
                    group_layout.addWidget(checkbox)
                    self.task_checkboxes[goal_id] = checkbox
                
                group.setLayout(group_layout)
                self.tasks_layout.addWidget(group)
        
        self.tasks_layout.addStretch()
    
    def on_task_toggle(self, goal_id: int):
        """Handle task completion toggle"""
        is_checked = self.task_checkboxes[goal_id].isChecked()
        
        if is_checked:
            self.db.mark_goal_complete(goal_id, self.today)
        else:
            self.db.mark_goal_incomplete(goal_id, self.today)
