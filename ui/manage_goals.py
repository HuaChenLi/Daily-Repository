import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ManageGoalsFrame(ttk.Frame):
    def __init__(self, parent, db, refresh_callback):
        super().__init__(parent)
        self.db = db
        self.refresh_callback = refresh_callback
        
        self.setup_ui()
    
    def center_window(self, window):
        """Center a dialog window on the parent window"""
        window.update_idletasks()
        
        # Get parent window (root)
        parent = self.master.master
        parent.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        window.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the UI for managing goals"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Manage Categories & Goals", font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        # Main content areas
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Categories section (left)
        cat_frame = ttk.LabelFrame(content_frame, text="Categories", padding=10)
        cat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Category buttons
        cat_btn_frame = ttk.Frame(cat_frame)
        cat_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(cat_btn_frame, text="+ Add Category", command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(cat_btn_frame, text="- Delete Selected", command=self.delete_category).pack(side=tk.LEFT, padx=5)
        
        # Category listbox with scrollbar
        cat_list_frame = ttk.Frame(cat_frame)
        cat_list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(cat_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_listbox = tk.Listbox(cat_list_frame, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.category_listbox.yview)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.category_listbox.bind('<<ListboxSelect>>', lambda e: self.on_category_selected())
        
        # Goals section (right)
        goal_frame = ttk.LabelFrame(content_frame, text="Goals in Selected Category", padding=10)
        goal_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Goal buttons
        goal_btn_frame = ttk.Frame(goal_frame)
        goal_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(goal_btn_frame, text="+ Add Goal", command=self.add_goal).pack(side=tk.LEFT, padx=5)
        ttk.Button(goal_btn_frame, text="- Delete Selected", command=self.delete_goal).pack(side=tk.LEFT, padx=5)
        
        # Goal listbox with scrollbar
        goal_list_frame = ttk.Frame(goal_frame)
        goal_list_frame.pack(fill=tk.BOTH, expand=True)
        
        goal_scrollbar = ttk.Scrollbar(goal_list_frame)
        goal_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.goal_listbox = tk.Listbox(goal_list_frame, yscrollcommand=goal_scrollbar.set)
        goal_scrollbar.config(command=self.goal_listbox.yview)
        self.goal_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.selected_category_id = None
        self.refresh()
    
    def refresh(self):
        """Refresh category and goal lists"""
        # Refresh categories
        self.category_listbox.delete(0, tk.END)
        self.goal_listbox.delete(0, tk.END)
        
        categories = self.db.get_categories()
        for cat_id, cat_name, _ in categories:
            self.category_listbox.insert(tk.END, cat_name)
        
        if categories:
            self.category_listbox.selection_set(0)
            self.selected_category_id = categories[0][0]
            self.on_category_selected()
    
    def on_category_selected(self):
        """Handle category selection"""
        selection = self.category_listbox.curselection()
        if selection:
            idx = selection[0]
            categories = self.db.get_categories()
            if idx < len(categories):
                self.selected_category_id = categories[idx][0]
                
                # Refresh goals
                self.goal_listbox.delete(0, tk.END)
                goals = self.db.get_goals_by_category(self.selected_category_id)
                for goal_id, goal_name in goals:
                    self.goal_listbox.insert(tk.END, goal_name)
    
    def add_category(self):
        """Add a new category"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Category")
        dialog.geometry("300x150")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Category Name:", font=("Arial", 12)).pack(padx=10, pady=(10, 0), anchor=tk.W)
        name_entry = ttk.Entry(dialog, width=40, font=("Arial", 12))
        name_entry.pack(padx=10, pady=5)
        name_entry.focus()
        
        self.center_window(dialog)
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Invalid Input", "Category name cannot be empty.", parent=dialog)
                return
            
            try:
                self.db.add_category(name)
                dialog.destroy()
                self.refresh()
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=dialog)
        
        ttk.Button(dialog, text="Save", command=save).pack(padx=10, pady=10)
    
    def delete_category(self):
        """Delete selected category"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Delete this category and all its goals?"):
            idx = selection[0]
            categories = self.db.get_categories()
            if idx < len(categories):
                cat_id = categories[idx][0]
                self.db.delete_category(cat_id)
                self.refresh()
    
    def add_goal(self):
        """Add a new goal"""
        if self.selected_category_id is None:
            messagebox.showwarning("No Category", "Please select or create a category first.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Add Goal")
        dialog.geometry("300x150")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Goal Name:", font=("Arial", 12)).pack(padx=10, pady=(10, 0), anchor=tk.W)
        name_entry = ttk.Entry(dialog, width=40, font=("Arial", 12))
        name_entry.pack(padx=10, pady=5)
        name_entry.focus()
        
        self.center_window(dialog)
        
        def save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Invalid Input", "Goal name cannot be empty.", parent=dialog)
                return
            
            self.db.add_goal(name, self.selected_category_id)
            dialog.destroy()
            self.on_category_selected()
            self.refresh_callback()
        
        ttk.Button(dialog, text="Save", command=save).pack(padx=10, pady=10)
    
    def delete_goal(self):
        """Delete selected goal"""
        selection = self.goal_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a goal to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Delete this goal? This will remove all completion records."):
            idx = selection[0]
            goals = self.db.get_goals_by_category(self.selected_category_id)
            if idx < len(goals):
                goal_id = goals[idx][0]
                self.db.delete_goal(goal_id)
                self.on_category_selected()
                self.refresh_callback()
