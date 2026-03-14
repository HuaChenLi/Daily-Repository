from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from .daily_tasks import DailyTasksTab
from .calendar_view import CalendarViewTab
from .statistics import StatisticsTab
from .manage_goals import ManageGoalsTab
import base64

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        self.setWindowTitle("Daily Achievements")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 700)
        
        # Restore window geometry if saved
        geometry = self.db.get_setting('window_geometry')
        if geometry:
            try:
                self.restoreGeometry(base64.b64decode(geometry))
            except:
                pass  # If invalid, use default
        
        # Create central widget with tab interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.daily_tab = DailyTasksTab(db, self.refresh_all)
        self.calendar_tab = CalendarViewTab(db, self.refresh_all)
        self.stats_tab = StatisticsTab(db, self.refresh_all)
        self.manage_tab = ManageGoalsTab(db, self.refresh_all)
        
        # Add tabs
        self.tabs.addTab(self.daily_tab, "Today's Tasks")
        self.tabs.addTab(self.calendar_tab, "Calendar")
        self.tabs.addTab(self.stats_tab, "Statistics")
        self.tabs.addTab(self.manage_tab, "Manage Goals")
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def refresh_all(self):
        """Refresh all tabs"""
        self.daily_tab.refresh()
        self.calendar_tab.refresh()
        self.stats_tab.refresh()
        self.manage_tab.refresh()
    
    def on_tab_changed(self, index):
        """Refresh the current tab when switched to"""
        if index == 0:
            self.daily_tab.refresh()
        elif index == 1:
            self.calendar_tab.refresh()
        elif index == 2:
            self.stats_tab.refresh()
        elif index == 3:
            self.manage_tab.refresh()
    
    def closeEvent(self, event):
        """Save window geometry before closing"""
        geometry = self.saveGeometry()
        self.db.set_setting('window_geometry', base64.b64encode(geometry).decode('utf-8'))
        event.accept()
