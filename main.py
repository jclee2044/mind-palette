import tkinter as tk
from tkinter import ttk
from ui_modules.train import TrainTab
from ui_modules.summarize import SummarizeTab
from ui_modules.chat import ChatTab
from ui_modules.colors import ColorsTab
from ui_modules.associations import AssociationsTab
from utils import set_database_update_callback


class SynesthesiaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MindPalette")
        self.geometry("800x600")
        
        # Cross-platform styling
        self.setup_cross_platform_styling()
        self.center_window()

        # --- Set app icon (title bar + taskbar) ---
        try:
            self.iconphoto(False, tk.PhotoImage(file="./icons/app_icon_no_border_w_shadow_padded_new_final.png"))
        except Exception as e:
            print(f"Could not load icon: {e}")

        # Create tabs
        self.notebook = ttk.Notebook(self)
        self.train_tab = ttk.Frame(self.notebook)
        self.summarize_tab = ttk.Frame(self.notebook)
        self.chat_tab = ttk.Frame(self.notebook)
        self.associations_tab = ttk.Frame(self.notebook)
        self.view_colors_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.train_tab, text="Train")
        self.notebook.add(self.summarize_tab, text="Summarize")
        self.notebook.add(self.chat_tab, text="Chat")
        self.notebook.add(self.view_colors_tab, text="Colors")
        self.notebook.add(self.associations_tab, text="Associations")
        self.notebook.pack(expand=1, fill="both")

        # Initialize tab modules after notebook is set up
        self.initialize_tab_modules()

    def setup_cross_platform_styling(self):
        """Set up consistent styling across platforms"""
        import platform
        
        # Store fonts for use in other modules (but don't override system defaults)
        if platform.system() == "Darwin":  # macOS
            self.default_font = ("SF Pro Display", 12)
            self.small_font = ("SF Pro Display", 10)
        elif platform.system() == "Windows":
            self.default_font = ("Segoe UI", 12)
            self.small_font = ("Segoe UI", 10)
        else:  # Linux and others
            self.default_font = ("DejaVu Sans", 12)
            self.small_font = ("DejaVu Sans", 10)

    def initialize_tab_modules(self):
        """Initialize all tab modules after the notebook is set up"""
        self.train_module = TrainTab(self.train_tab)
        self.summarize_module = SummarizeTab(self.summarize_tab, self.refresh_all_tabs)
        self.chat_module = ChatTab(self.chat_tab, self.refresh_all_tabs)
        self.colors_module = ColorsTab(self.view_colors_tab)
        self.associations_module = AssociationsTab(self.associations_tab, self.refresh_associations)
        
        # Set up database update callback
        set_database_update_callback(self.refresh_associations)
        
        # Initial refresh of associations table
        self.refresh_associations()

    def refresh_all_tabs(self):
        """Refresh all tabs that depend on API key availability"""
        self.summarize_module.setup_ui()
        self.chat_module.setup_ui()

    def refresh_associations(self):
        """Refresh the associations table"""
        if hasattr(self, 'associations_module'):
            self.associations_module.refresh_table()

    def center_window(self):
        self.update_idletasks()
        width = 800
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")


if __name__ == "__main__":
    app = SynesthesiaApp()
    app.mainloop() 