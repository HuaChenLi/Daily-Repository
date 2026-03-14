from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QListWidget, QListWidgetItem, QDialog, QLineEdit, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ManageGoalsTab(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.selected_category_id = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Manage Categories & Goals")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(header)
        
        # Main content with two columns
        content_layout = QHBoxLayout()
        
        # Categories section
        cat_group_layout = QVBoxLayout()
        cat_label = QLabel("Categories")
        cat_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        cat_group_layout.addWidget(cat_label)
        
        cat_btn_layout = QHBoxLayout()
        cat_btn_layout.addWidget(QPushButton("+ Add", clicked=self.add_category))
        cat_btn_layout.addWidget(QPushButton("- Delete", clicked=self.delete_category))
        cat_group_layout.addLayout(cat_btn_layout)
        
        self.category_list = QListWidget()
        self.category_list.setFont(QFont("Segoe UI", 11))
        self.category_list.itemSelectionChanged.connect(self.on_category_selected)
        cat_group_layout.addWidget(self.category_list)
        
        content_layout.addLayout(cat_group_layout)
        
        # Goals section
        goal_group_layout = QVBoxLayout()
        goal_label = QLabel("Goals in Selected Category")
        goal_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        goal_group_layout.addWidget(goal_label)
        
        goal_btn_layout = QHBoxLayout()
        goal_btn_layout.addWidget(QPushButton("+ Add", clicked=self.add_goal))
        goal_btn_layout.addWidget(QPushButton("- Delete", clicked=self.delete_goal))
        goal_group_layout.addLayout(goal_btn_layout)
        
        self.goal_list = QListWidget()
        self.goal_list.setFont(QFont("Segoe UI", 11))
        goal_group_layout.addWidget(self.goal_list)
        
        content_layout.addLayout(goal_group_layout)
        
        layout.addLayout(content_layout)
        self.setLayout(layout)
        
        self.refresh()
    
    def refresh(self):
        """Refresh category and goal lists"""
        self.category_list.clear()
        self.goal_list.clear()
        
        categories = self.db.get_categories()
        for cat_id, cat_name, _ in categories:
            self.category_list.addItem(cat_name)
        
        if categories:
            self.category_list.setCurrentRow(0)
            self.selected_category_id = categories[0][0]
            self.on_category_selected()
    
    def on_category_selected(self):
        """Handle category selection"""
        categories = self.db.get_categories()
        current_row = self.category_list.currentRow()
        
        if current_row >= 0 and current_row < len(categories):
            self.selected_category_id = categories[current_row][0]
            
            self.goal_list.clear()
            goals = self.db.get_goals_by_category(self.selected_category_id)
            for goal_id, goal_name in goals:
                self.goal_list.addItem(goal_name)
    
    def add_category(self):
        """Add a new category"""
        dialog = CategoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            if name:
                try:
                    self.db.add_category(name)
                    self.refresh()
                except ValueError as e:
                    QMessageBox.critical(self, "Error", str(e))
    
    def delete_category(self):
        """Delete selected category"""
        if self.category_list.currentRow() < 0:
            QMessageBox.warning(self, "No Selection", "Please select a category to delete.")
            return
        
        if QMessageBox.question(self, "Confirm", "Delete this category and all its goals?") == QMessageBox.Yes:
            categories = self.db.get_categories()
            idx = self.category_list.currentRow()
            if idx < len(categories):
                self.db.delete_category(categories[idx][0])
                self.refresh()
    
    def add_goal(self):
        """Add a new goal"""
        if self.selected_category_id is None:
            QMessageBox.warning(self, "No Category", "Please select or create a category first.")
            return
        
        dialog = GoalDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            if name:
                self.db.add_goal(name, self.selected_category_id)
                self.on_category_selected()
                self.refresh_callback()
    
    def delete_goal(self):
        """Delete selected goal"""
        if self.goal_list.currentRow() < 0:
            QMessageBox.warning(self, "No Selection", "Please select a goal to delete.")
            return
        
        if QMessageBox.question(self, "Confirm", "Delete this goal? This will remove all completion records.") == QMessageBox.Yes:
            goals = self.db.get_goals_by_category(self.selected_category_id)
            idx = self.goal_list.currentRow()
            if idx < len(goals):
                self.db.delete_goal(goals[idx][0])
                self.on_category_selected()
                self.refresh_callback()


class CategoryDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Category")
        self.setGeometry(0, 0, 300, 150)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Category Name:"))
        self.text_input = QLineEdit()
        self.text_input.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.text_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(QPushButton("Save", clicked=self.accept))
        btn_layout.addWidget(QPushButton("Cancel", clicked=self.reject))
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.text_input.setFocus()
        
        # Center dialog on parent window
        self.center_on_parent(parent)
    
    def center_on_parent(self, parent):
        """Center dialog on parent window"""
        if parent:
            parent_geometry = parent.geometry()
            dialog_width = self.width()
            dialog_height = self.height()
            
            x = parent_geometry.x() + (parent_geometry.width() - dialog_width) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_height) // 2
            
            self.move(x, y)
    
    def get_name(self):
        return self.text_input.text().strip()


class GoalDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Goal")
        self.setGeometry(0, 0, 300, 150)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Goal Name:"))
        self.text_input = QLineEdit()
        self.text_input.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.text_input)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(QPushButton("Save", clicked=self.accept))
        btn_layout.addWidget(QPushButton("Cancel", clicked=self.reject))
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.text_input.setFocus()
        
        # Center dialog on parent window
        self.center_on_parent(parent)
    
    def center_on_parent(self, parent):
        """Center dialog on parent window"""
        if parent:
            parent_geometry = parent.geometry()
            dialog_width = self.width()
            dialog_height = self.height()
            
            x = parent_geometry.x() + (parent_geometry.width() - dialog_width) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_height) // 2
            
            self.move(x, y)
    
    def get_name(self):
        return self.text_input.text().strip()
