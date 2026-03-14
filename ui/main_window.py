import tkinter as tk
from tkinter import ttk
from .daily_tasks import DailyTasksFrame
from .calendar_view import CalendarViewFrame
from .statistics import StatisticsFrame
from .manage_goals import ManageGoalsFrame

class MainWindow:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        
        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Daily Tasks
        self.daily_frame = DailyTasksFrame(self.notebook, db)
        self.notebook.add(self.daily_frame, text="Today's Tasks")
        
        # Tab 2: Calendar View
        self.calendar_frame = CalendarViewFrame(self.notebook, db)
        self.notebook.add(self.calendar_frame, text="Calendar")
        
        # Tab 3: Statistics
        self.stats_frame = StatisticsFrame(self.notebook, db)
        self.notebook.add(self.stats_frame, text="Statistics")
        
        # Tab 4: Manage Goals
        self.manage_frame = ManageGoalsFrame(self.notebook, db, self.refresh_all)
        self.notebook.add(self.manage_frame, text="Manage Goals")
        
        # Bind tab change to refresh data
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def refresh_all(self):
        """Refresh all tabs"""
        self.daily_frame.refresh()
        self.calendar_frame.refresh()
        self.stats_frame.refresh()
        self.manage_frame.refresh()
    
    def on_tab_changed(self, event):
        """Refresh the current tab when switched to"""
        current_tab = self.notebook.select()
        tab_index = self.notebook.index(current_tab)
        
        if tab_index == 0:
            self.daily_frame.refresh()
        elif tab_index == 1:
            self.calendar_frame.refresh()
        elif tab_index == 2:
            self.stats_frame.refresh()
        elif tab_index == 3:
            self.manage_frame.refresh()
