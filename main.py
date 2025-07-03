import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import LabDatabase
from gui.main_window import MainWindow

class LabBillingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Laboratory Billing System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Set window icon (optional)
        try:
            self.root.iconbitmap("icon.ico")  # Add icon file if available
        except:
            pass
        
        # Initialize database
        try:
            self.db = LabDatabase()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            sys.exit(1)
        
        # Initialize main window
        self.main_window = MainWindow(self.root, self.db)
        
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()

def main():
    """Main entry point"""
    app = LabBillingApp()
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.run()

if __name__ == "__main__":
    main() 