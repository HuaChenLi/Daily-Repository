from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QFrame)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QPen, QMouseEvent
from datetime import datetime, timedelta
import calendar as cal
from typing import Optional
class CalendarViewTab(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback
        self.current_date = datetime.now()
        self.selected_goal = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Control area
        control_layout = QHBoxLayout()
        
        # Month navigation
        prev_btn = QPushButton("< Previous")
        prev_btn.clicked.connect(self.prev_month)
        control_layout.addWidget(prev_btn)
        self.month_label = QLabel("")
        self.month_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.month_label.setMinimumWidth(200)
        control_layout.addWidget(self.month_label)
        next_btn = QPushButton("Next >")
        next_btn.clicked.connect(self.next_month)
        control_layout.addWidget(next_btn)
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.today_month)
        control_layout.addWidget(today_btn)
        
        # Goal selector
        control_layout.addSpacing(20)
        control_layout.addWidget(QLabel("Select Goal:"))
        self.goal_combo = QComboBox()
        self.goal_combo.setFont(QFont("Segoe UI", 9))
        self.goal_combo.setMinimumWidth(300)
        self.goal_combo.currentIndexChanged.connect(self.on_goal_selected)
        control_layout.addWidget(self.goal_combo)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Calendar canvas
        self.calendar_canvas = CalendarCanvas(self.db, self)
        self.calendar_canvas.setMinimumHeight(400)
        layout.addWidget(self.calendar_canvas)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("✓ = Completed on that day"))
        legend_layout.addWidget(QLabel("Empty = Not completed"))
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        self.setLayout(layout)
        self.refresh()
    
    def refresh(self):
        """Refresh calendar with goal data"""
        goals = self.db.get_all_goals()
        goal_names = [name for _, name, _ in goals]
        
        self.goal_combo.blockSignals(True)
        self.goal_combo.clear()
        self.goal_combo.addItems(goal_names)
        self.goal_combo.blockSignals(False)
        
        if goal_names:
            self.goal_combo.setCurrentIndex(0)
            self.selected_goal = goals[0][0]
        
        self.update_calendar()
    
    def on_goal_selected(self):
        """Handle goal selection"""
        goals = self.db.get_all_goals()
        idx = self.goal_combo.currentIndex()
        if idx >= 0 and idx < len(goals):
            self.selected_goal = goals[idx][0]
            self.update_calendar()
    
    def prev_month(self):
        """Go to previous month"""
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.update_calendar()
    
    def next_month(self):
        """Go to next month"""
        last_day = cal.monthrange(self.current_date.year, self.current_date.month)[1]
        self.current_date = self.current_date.replace(day=last_day) + timedelta(days=1)
        self.update_calendar()
    
    def today_month(self):
        """Go to today's month"""
        self.current_date = datetime.now()
        self.update_calendar()
    
    def update_calendar(self):
        """Update calendar display"""
        self.month_label.setText(self.current_date.strftime("%B %Y"))
        self.calendar_canvas.update_calendar(self.current_date, self.selected_goal)


class CalendarCanvas(QFrame):
    def __init__(self, db, parent: CalendarViewTab):
        super().__init__()
        self.db = db
        self.calendar_view: CalendarViewTab = parent
        self.current_date = datetime.now()
        self.selected_goal = None
        self.setStyleSheet("background-color: white; border: 1px solid gray;")
    
    def update_calendar(self, current_date, selected_goal):
        """Update calendar data"""
        self.current_date = current_date
        self.selected_goal = selected_goal
        self.update()
    
    def paintEvent(self, a0):
        """Paint calendar"""
        if not self.selected_goal:
            return
        
        painter = QPainter(self)
        painter.setFont(QFont("Segoe UI", 9))
        
        width = self.width()
        height = self.height()
        
        # Get calendar grid
        year = self.current_date.year
        month = self.current_date.month
        month_calendar = cal.monthcalendar(year, month)
        weekdays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
        
        # Get completed dates
        completed_dates = set(self.db.get_completed_dates_for_goal(self.selected_goal))
        
        # Calculate cell size
        cell_width = width / 7
        cell_height = height / (len(month_calendar) + 1)
        
        # Draw weekday headers
        for i, weekday in enumerate(weekdays):
            x = i * cell_width
            y = 0
            
            painter.fillRect(int(x), int(y), int(cell_width), int(cell_height),
                           QBrush(QColor("#e0e0e0")))
            painter.drawRect(int(x), int(y), int(cell_width), int(cell_height))
            
            painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
            painter.drawText(int(x), int(y), int(cell_width), int(cell_height),
                           0x84, weekday)
        
        # Draw calendar days
        for week_idx, week in enumerate(month_calendar):
            for day_idx, day in enumerate(week):
                x = day_idx * cell_width
                y = (week_idx + 1) * cell_height
                
                if day == 0:
                    painter.fillRect(int(x), int(y), int(cell_width), int(cell_height),
                                   QBrush(QColor("white")))
                    painter.setPen(QPen(QColor("gray")))
                else:
                    date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    is_completed = date_str in completed_dates
                    
                    bg_color = "#90EE90" if is_completed else "white"
                    painter.fillRect(int(x), int(y), int(cell_width), int(cell_height),
                                   QBrush(QColor(bg_color)))
                    painter.setPen(QPen(QColor("gray")))
                
                painter.drawRect(int(x), int(y), int(cell_width), int(cell_height))
                
                if day != 0:
                    # Day number
                    painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                    painter.setPen(QPen(QColor("black")))
                    painter.drawText(int(x + 5), int(y + 5), int(cell_width - 10),
                                   int(cell_height - 10), 0x20 | 0x1, str(day))
                    
                    # Checkmark if completed
                    date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    if date_str in completed_dates:
                        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
                        painter.setPen(QPen(QColor("green")))
                        painter.drawText(int(x), int(y), int(cell_width), int(cell_height),
                                       0x40 | 0x2, "✓")
    
    def mouseDoubleClickEvent(self, a0: Optional[QMouseEvent]):
        """Handle double-click to toggle completion"""
        if a0 is None or not self.calendar_view.selected_goal:
            return
        
        width = self.width()
        height = self.height()
        
        year = self.current_date.year
        month = self.current_date.month
        month_calendar = cal.monthcalendar(year, month)
        
        cell_width = width / 7
        cell_height = height / (len(month_calendar) + 1)
        
        # Figure out which cell was clicked
        day_idx = int(a0.x() / cell_width)
        week_idx = int((a0.y() - cell_height) / cell_height)
        
        # Bounds check
        if week_idx < 0 or week_idx >= len(month_calendar) or day_idx < 0 or day_idx >= 7:
            return
        
        day = month_calendar[week_idx][day_idx]
        
        if day == 0:
            return
        
        # Build date string
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Toggle completion
        is_completed = self.db.is_goal_completed(self.calendar_view.selected_goal, date_str)
        
        if is_completed:
            self.db.mark_goal_incomplete(self.calendar_view.selected_goal, date_str)
        else:
            self.db.mark_goal_complete(self.calendar_view.selected_goal, date_str)
        
        self.update()
