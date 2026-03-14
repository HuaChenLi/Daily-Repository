import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from database import Database
from ui.main_window import MainWindow

def main():
    # Initialize database in user's home directory
    app_data_dir = Path.home() / "AppData" / "Local" / "DailyAchievements"
    app_data_dir.mkdir(parents=True, exist_ok=True)
    db_path = app_data_dir / 'achievements.db'
    
    db = Database(str(db_path))
    
    # Create PyQt5 application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow(db)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
