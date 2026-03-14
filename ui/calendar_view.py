import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar as cal

class CalendarViewFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.current_date = datetime.now()
        self.selected_goal = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for calendar view"""
        # Top control area
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Month/Year navigation
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(nav_frame, text="< Previous", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        self.month_label = ttk.Label(nav_frame, text="", font=("Arial", 14, "bold"), width=20)
        self.month_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Next >", command=self.next_month).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Today", command=self.today_month).pack(side=tk.LEFT, padx=5)
        
        # Goal selector
        selector_frame = ttk.Frame(control_frame)
        selector_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(selector_frame, text="Select Goal:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.goal_combo = ttk.Combobox(selector_frame, state="readonly", width=30, font=("Arial", 11))
        self.goal_combo.pack(side=tk.LEFT, padx=5)
        self.goal_combo.bind("<<ComboboxSelected>>", lambda e: self.on_goal_selected())
        
        # Calendar area
        calendar_frame = ttk.Frame(self)
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.calendar_canvas = tk.Canvas(calendar_frame, bg="white", highlightthickness=1, highlightbackground="gray")
        self.calendar_canvas.pack(fill=tk.BOTH, expand=True)
        self.calendar_canvas.bind("<Configure>", lambda e: self.draw_calendar())
        self.calendar_canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        
        # Legend
        legend_frame = ttk.Frame(self)
        legend_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(legend_frame, text="✓ = Completed on that day", font=("Arial", 11)).pack(anchor=tk.W)
        ttk.Label(legend_frame, text="Empty = Not completed", font=("Arial", 11)).pack(anchor=tk.W)
        
        self.refresh()
    
    def refresh(self):
        """Refresh calendar with goal data"""
        goals = self.db.get_all_goals()
        goal_names = [f"{name}" for _, name, _ in goals]
        
        self.goal_combo['values'] = goal_names
        
        if goal_names:
            self.goal_combo.current(0)
            self.selected_goal = goals[0][0]
        
        self.draw_calendar()
    
    def on_goal_selected(self):
        """Handle goal selection"""
        goals = self.db.get_all_goals()
        idx = self.goal_combo.current()
        if idx >= 0:
            self.selected_goal = goals[idx][0]
            self.draw_calendar()
    
    def prev_month(self):
        """Go to previous month"""
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.draw_calendar()
    
    def next_month(self):
        """Go to next month"""
        last_day = cal.monthrange(self.current_date.year, self.current_date.month)[1]
        self.current_date = self.current_date.replace(day=last_day) + timedelta(days=1)
        self.draw_calendar()
    
    def today_month(self):
        """Go to today's month"""
        self.current_date = datetime.now()
        self.draw_calendar()
    
    def on_canvas_double_click(self, event):
        """Handle double-click on calendar cell to toggle completion"""
        if not self.selected_goal:
            return
        
        width = self.calendar_canvas.winfo_width()
        height = self.calendar_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Get calendar grid for current month
        month_calendar = cal.monthcalendar(self.current_date.year, self.current_date.month)
        cell_width = width / 7
        cell_height = height / (len(month_calendar) + 1)
        
        # Figure out which cell was clicked
        day_idx = int(event.x / cell_width)
        week_idx = int((event.y - cell_height) / cell_height)
        
        # Bounds check
        if week_idx < 0 or week_idx >= len(month_calendar) or day_idx < 0 or day_idx >= 7:
            return
        
        day = month_calendar[week_idx][day_idx]
        
        if day == 0:
            return
        
        # Build the date string
        year = self.current_date.year
        month = self.current_date.month
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Toggle completion
        is_completed = self.db.is_goal_completed(self.selected_goal, date_str)
        
        if is_completed:
            self.db.mark_goal_incomplete(self.selected_goal, date_str)
        else:
            self.db.mark_goal_complete(self.selected_goal, date_str)
        
        # Redraw calendar
        self.draw_calendar()
    
    def draw_calendar(self):
        """Draw the calendar with completed days marked"""
        self.calendar_canvas.delete("all")
        
        if not self.selected_goal:
            return
        
        width = self.calendar_canvas.winfo_width()
        height = self.calendar_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Update month label
        self.month_label.config(text=self.current_date.strftime("%B %Y"))
        
        # Get completed dates for this goal
        completed_dates = set(self.db.get_completed_dates_for_goal(self.selected_goal))
        
        # Calendar parameters
        year = self.current_date.year
        month = self.current_date.month
        
        # Get calendar grid
        month_calendar = cal.monthcalendar(year, month)
        weekdays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        
        # Calculate cell size
        cell_width = width / 7
        cell_height = height / (len(month_calendar) + 1)
        
        # Draw weekday headers
        for i, weekday in enumerate(weekdays):
            x = i * cell_width
            y = 0
            self.calendar_canvas.create_rectangle(
                x, y, x + cell_width, y + cell_height,
                fill="#e0e0e0", outline="gray"
            )
            self.calendar_canvas.create_text(
                x + cell_width / 2, y + cell_height / 2,
                text=weekday, font=("Arial", 12, "bold")
            )
        # Draw calendar days
        for week_idx, week in enumerate(month_calendar):
            for day_idx, day in enumerate(week):
                x = day_idx * cell_width
                y = (week_idx + 1) * cell_height
                
                if day == 0:
                    # Empty cell
                    self.calendar_canvas.create_rectangle(
                        x, y, x + cell_width, y + cell_height,
                        fill="white", outline="lightgray"
                    )
                else:
                    # Check if completed
                    date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    is_completed = date_str in completed_dates
                    
                    bg_color = "#90EE90" if is_completed else "white"
                    
                    self.calendar_canvas.create_rectangle(
                        x, y, x + cell_width, y + cell_height,
                        fill=bg_color, outline="gray"
                    )
                    
                    # Day number
                    self.calendar_canvas.create_text(
                        x + 15, y + 15,
                        text=str(day), font=("Arial", 14, "bold")
                    )
                    
                    # Checkmark if completed
                    if is_completed:
                        self.calendar_canvas.create_text(
                            x + cell_width - 15, y + cell_height - 15,
                            text="✓", font=("Arial", 16, "bold"), fill="green"
                        )
