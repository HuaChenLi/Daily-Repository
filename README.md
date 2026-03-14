# Daily Achievements - Task Management GUI

A Python GUI application to track daily goals and view completion history in a calendar.

## Features

- **Daily Task Checklist**: Check off tasks you've completed today
- **Task Categories**: Organize goals by categories (e.g., Exercise, Reading, Work)
- **Calendar View**: See which days you completed each task
- **Statistics**: View tallies showing how many days each goal has been completed
- **Persistent Storage**: All data saved to SQLite database

## Requirements

- Python 3.7+
- Tkinter (usually included with Python)

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Run: `python main.py`

## Usage

### Today's Tasks Tab
- Check off tasks you've completed today
- Tasks are organized by category

### Calendar Tab
- Select a goal to see a calendar of completed days
- Green highlighted days with ✓ mark show completion
- Navigate between months

### Statistics Tab
- View overall statistics
- See breakdown by category
- View tally of how many days each goal was completed

### Manage Goals Tab
- Create new categories
- Add goals to categories
- Delete categories or goals

## File Structure

```
Achievements/
├── main.py                 # Entry point
├── database.py            # SQLite database operations
├── achievements.db        # Database file (created on first run)
└── ui/
    ├── __init__.py
    ├── main_window.py     # Main tabbed interface
    ├── daily_tasks.py     # Today's tasks with checkboxes
    ├── calendar_view.py   # Calendar visualization
    ├── statistics.py      # Statistics and tallies
    └── manage_goals.py    # Add/delete categories and goals
```

## Database

The application uses SQLite to store:
- **Categories**: Goal categories with colors
- **Goals**: Individual goals/tasks with category association
- **Completions**: Records of when goals were completed

The database file (`achievements.db`) is created automatically on first run.

## How It Works

1. **Create Categories**: Use the "Manage Goals" tab to add categories (e.g., "Fitness", "Learning")
2. **Add Goals**: For each category, add specific goals (e.g., "Run 5km", "Read 30 minutes")
3. **Mark Completion**: In "Today's Tasks", check off goals you've completed
4. **Track Progress**: View the calendar to see completed days and statistics for trends

## Tips

- Create broad categories to keep things organized
- Use specific goal names for clarity
- Check the calendar monthly to see patterns
- Review statistics regularly to track progress

---

Enjoy tracking your daily achievements! 🎯
