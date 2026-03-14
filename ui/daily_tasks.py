import tkinter as tk
from tkinter import ttk
from datetime import datetime

class DailyTasksFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.task_vars = {}  # goal_id -> BooleanVar mapping
        self.checkboxes = {}  # goal_id -> checkbox widget mapping
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for daily tasks"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"Tasks for {self.today}", font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        # Main content area with scrollbar
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scrollable_frame = scrollable_frame
        self.refresh()
    
    def refresh(self):
        """Refresh the task list"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.task_vars.clear()
        self.checkboxes.clear()
        
        # Get all goals grouped by category
        categories = self.db.get_categories()
        
        if not categories:
            ttk.Label(self.scrollable_frame, text="No categories yet. Add one in 'Manage Goals' tab.").pack(padx=10, pady=10)
            return
        
        # Display tasks by category
        for cat_id, cat_name, cat_color in categories:
            goals = self.db.get_goals_by_category(cat_id)
            
            if goals:
                # Category header
                cat_header = ttk.LabelFrame(self.scrollable_frame, text=cat_name, padding=10)
                cat_header.pack(fill=tk.X, padx=10, pady=5)
                
                # Tasks in category
                for goal_id, goal_name in goals:
                    is_completed = self.db.is_goal_completed(goal_id, self.today)
                    
                    task_var = tk.BooleanVar(value=is_completed)
                    self.task_vars[goal_id] = task_var
                    
                    # Create checkbox
                    checkbox = ttk.Checkbutton(
                        cat_header,
                        text=goal_name,
                        variable=task_var,
                        command=lambda gid=goal_id: self.on_task_toggle(gid)
                    )
                    checkbox.pack(anchor=tk.W, padx=10, pady=3)
                    self.checkboxes[goal_id] = checkbox
    
    def on_task_toggle(self, goal_id: int):
        """Handle task completion toggle"""
        is_checked = self.task_vars[goal_id].get()
        
        if is_checked:
            self.db.mark_goal_complete(goal_id, self.today)
        else:
            self.db.mark_goal_incomplete(goal_id, self.today)
