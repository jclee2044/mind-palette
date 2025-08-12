import tkinter as tk
from tkinter import ttk
from ui_modules.train import TrainTab
from ui_modules.summarize import SummarizeTab
from ui_modules.chat import ChatTab
from ui_modules.colors import ColorsTab
from ui_modules.associations import AssociationsTab


class SynesthesiaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mind Palette")
        self.geometry("800x600")
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

        # Initialize tab modules
        self.train_module = TrainTab(self.train_tab)
        self.summarize_module = SummarizeTab(self.summarize_tab)
        self.chat_module = ChatTab(self.chat_tab)
        self.colors_module = ColorsTab(self.view_colors_tab)
        self.associations_module = AssociationsTab(self.associations_tab)

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