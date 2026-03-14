import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
import os
from database import Database
from ui.main_window import MainWindow

def main():
    # Initialize database
    db_path = os.path.join(os.path.dirname(__file__), 'achievements.db')
    db = Database(db_path)
    
    # Create main window
    root = tk.Tk()
    root.title("Daily Achievements")
    root.geometry("1000x700")
    root.minsize(800, 600)
    
    # Initialize main window UI
    app = MainWindow(root, db)
    
    root.mainloop()

if __name__ == "__main__":
    main()
