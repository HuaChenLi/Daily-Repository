import tkinter as tk
from tkinter import ttk

class StatisticsFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for statistics"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Statistics & Tallies", font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Refresh", command=self.refresh).pack(side=tk.RIGHT, padx=5)
        
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
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scrollable_frame = scrollable_frame
        self.refresh()
    
    def refresh(self):
        """Refresh statistics"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Category statistics
        cat_stats = self.db.get_category_stats()
        
        if not cat_stats:
            ttk.Label(self.scrollable_frame, text="No data yet. Add categories and goals to see statistics.").pack(padx=10, pady=10)
            return
        
        # Overall stats
        total_completions = sum(stats['total_days'] for stats in cat_stats.values())
        total_goals = sum(stats['goal_count'] for stats in cat_stats.values())
        
        overall_frame = ttk.LabelFrame(self.scrollable_frame, text="Overall Statistics", padding=15)
        overall_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(overall_frame, text=f"Total Goals: {total_goals}", font=("Arial", 13)).pack(anchor=tk.W, pady=3)
        ttk.Label(overall_frame, text=f"Total Completion Days: {total_completions}", font=("Arial", 13)).pack(anchor=tk.W, pady=3)
        
        # Category breakdown
        ttk.Label(self.scrollable_frame, text="By Category", font=("Arial", 14, "bold")).pack(anchor=tk.W, padx=10, pady=(20, 10))
        
        for cat_name, stats in sorted(cat_stats.items()):
            cat_frame = ttk.LabelFrame(self.scrollable_frame, text=cat_name, padding=10)
            cat_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(cat_frame, text=f"Goals: {stats['goal_count']}", font=("Arial", 12)).pack(anchor=tk.W, pady=2)
            ttk.Label(cat_frame, text=f"Completion Days: {stats['total_days']}", font=("Arial", 12)).pack(anchor=tk.W, pady=2)
        
        # Goal-specific tallies
        ttk.Label(self.scrollable_frame, text="Goal Tallies", font=("Arial", 14, "bold")).pack(anchor=tk.W, padx=10, pady=(20, 10))
        
        goals = self.db.get_all_goals()
        
        if goals:
            goal_tallies = []
            for goal_id, goal_name, _ in goals:
                count = self.db.get_completion_tally(goal_id)
                goal_tallies.append((goal_name, count))
            
            goal_tallies.sort(key=lambda x: x[1], reverse=True)
            
            for goal_name, count in goal_tallies:
                goal_frame = ttk.Frame(self.scrollable_frame)
                goal_frame.pack(fill=tk.X, padx=20, pady=3)
                
                ttk.Label(goal_frame, text=f"{goal_name}", font=("Arial", 12), width=30, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(goal_frame, text=f"{count} days", font=("Arial", 12, "bold"), foreground="blue").pack(side=tk.RIGHT)
        else:
            ttk.Label(self.scrollable_frame, text="No goals yet.", foreground="gray").pack(padx=20, pady=5)
