from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QGroupBox, QScrollArea)
from PyQt5.QtGui import QFont

class StatisticsTab(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Header with refresh button
        header_layout = QVBoxLayout()
        header_label = QLabel("Statistics & Tallies")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(header_label)
        layout.addLayout(header_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        self.refresh()
    
    def refresh(self):
        """Refresh statistics"""
        # Clear existing widgets
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        
        # Category statistics
        cat_stats = self.db.get_category_stats()
        
        if not cat_stats:
            label = QLabel("No data yet. Add categories and goals to see statistics.")
            self.scroll_layout.addWidget(label)
            return
        
        # Overall stats
        total_completions = sum(stats['total_days'] for stats in cat_stats.values())
        total_goals = sum(stats['goal_count'] for stats in cat_stats.values())
        
        overall_group = QGroupBox("Overall Statistics")
        overall_group.setFont(QFont("Segoe UI", 11))
        overall_layout = QVBoxLayout()
        total_goals_label = QLabel(f"Total Goals: {total_goals}")
        total_goals_label.setFont(QFont("Segoe UI", 9))
        overall_layout.addWidget(total_goals_label)
        total_days_label = QLabel(f"Total Completion Days: {total_completions}")
        total_days_label.setFont(QFont("Segoe UI", 9))
        overall_layout.addWidget(total_days_label)
        overall_group.setLayout(overall_layout)
        self.scroll_layout.addWidget(overall_group)
        
        # Category breakdown
        category_label = QLabel("By Category")
        category_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.scroll_layout.addWidget(category_label)
        
        for cat_name, stats in sorted(cat_stats.items()):
            cat_group = QGroupBox(cat_name)
            cat_group.setFont(QFont("Segoe UI", 11))
            cat_layout = QVBoxLayout()
            goals_label = QLabel(f"Goals: {stats['goal_count']}")
            goals_label.setFont(QFont("Segoe UI", 9))
            cat_layout.addWidget(goals_label)
            days_label = QLabel(f"Completion Days: {stats['total_days']}")
            days_label.setFont(QFont("Segoe UI", 9))
            cat_layout.addWidget(days_label)
            cat_group.setLayout(cat_layout)
            self.scroll_layout.addWidget(cat_group)
        
        # Goal tallies
        tally_label = QLabel("Goal Tallies")
        tally_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.scroll_layout.addWidget(tally_label)
        
        goals = self.db.get_all_goals()
        if goals:
            goal_tallies = []
            for goal_id, goal_name, _ in goals:
                count = self.db.get_completion_tally(goal_id)
                goal_tallies.append((goal_name, count))
            
            goal_tallies.sort(key=lambda x: x[1], reverse=True)
            
            for goal_name, count in goal_tallies:
                label = QLabel(f"{goal_name}: {count} days")
                label.setFont(QFont("Segoe UI", 9))
                self.scroll_layout.addWidget(label)
        
        self.scroll_layout.addStretch()
