import sys
import os
from PyQt5.QtWidgets import QApplication
from database import Database
from ui.main_window import MainWindow

def main():
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), 'achievements.db')
    db = Database(db_path)
    
    # Create PyQt5 application
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = MainWindow(db)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
