import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#3498db',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Goals/Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # Completions table - tracks when goals are completed
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                completed_date DATE NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES goals(id)
                    ON DELETE CASCADE,
                UNIQUE(goal_id, completed_date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_category(self, name: str, color: str = '#3498db') -> int:
        """Add a new category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO categories (name, color) VALUES (?, ?)',
                (name, color)
            )
            conn.commit()
            category_id = cursor.lastrowid
            assert category_id is not None
            conn.close()
            return category_id
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Category '{name}' already exists")
    
    def get_categories(self) -> List[Tuple[int, str, str]]:
        """Get all categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, color FROM categories ORDER BY name')
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    def delete_category(self, category_id: int):
        """Delete a category and all its goals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        conn.commit()
        conn.close()
    
    def add_goal(self, name: str, category_id: int) -> int:
        """Add a new goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO goals (name, category_id) VALUES (?, ?)',
            (name, category_id)
        )
        conn.commit()
        goal_id = cursor.lastrowid
        assert goal_id is not None
        conn.close()
        return goal_id
    
    def get_goals_by_category(self, category_id: int) -> List[Tuple[int, str]]:
        """Get all goals in a category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name FROM goals WHERE category_id = ? ORDER BY name',
            (category_id,)
        )
        goals = cursor.fetchall()
        conn.close()
        return goals
    
    def get_all_goals(self) -> List[Tuple[int, str, int]]:
        """Get all goals with their category ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT g.id, g.name, g.category_id FROM goals g ORDER BY g.name'
        )
        goals = cursor.fetchall()
        conn.close()
        return goals
    
    def delete_goal(self, goal_id: int):
        """Delete a goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
        conn.commit()
        conn.close()
    
    def mark_goal_complete(self, goal_id: int, date: str) -> bool:
        """Mark a goal as complete for a specific date (YYYY-MM-DD format)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO completions (goal_id, completed_date) VALUES (?, ?)',
                (goal_id, date)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def mark_goal_incomplete(self, goal_id: int, date: str):
        """Mark a goal as incomplete for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM completions WHERE goal_id = ? AND completed_date = ?',
            (goal_id, date)
        )
        conn.commit()
        conn.close()
    
    def is_goal_completed(self, goal_id: int, date: str) -> bool:
        """Check if a goal is completed on a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM completions WHERE goal_id = ? AND completed_date = ?',
            (goal_id, date)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_completions_for_date(self, date: str) -> List[int]:
        """Get all completed goal IDs for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT goal_id FROM completions WHERE completed_date = ?',
            (date,)
        )
        goals = [row[0] for row in cursor.fetchall()]
        conn.close()
        return goals
    
    def get_completion_tally(self, goal_id: int) -> int:
        """Get total number of days a goal was completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) FROM completions WHERE goal_id = ?',
            (goal_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_completed_dates_for_goal(self, goal_id: int) -> List[str]:
        """Get all dates when a goal was completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT completed_date FROM completions WHERE goal_id = ? ORDER BY completed_date',
            (goal_id,)
        )
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates
    
    def get_category_stats(self) -> Dict:
        """Get statistics per category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        cursor.execute('SELECT id, name FROM categories')
        for cat_id, cat_name in cursor.fetchall():
            cursor.execute(
                '''SELECT COUNT(DISTINCT completed_date) FROM completions c
                   JOIN goals g ON c.goal_id = g.id
                   WHERE g.category_id = ?''',
                (cat_id,)
            )
            total_days = cursor.fetchone()[0]
            
            cursor.execute(
                'SELECT COUNT(*) FROM goals WHERE category_id = ?',
                (cat_id,)
            )
            goal_count = cursor.fetchone()[0]
            
            stats[cat_name] = {'total_days': total_days, 'goal_count': goal_count}
        
        conn.close()
        return stats
