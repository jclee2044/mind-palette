import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import os

from ui_modules.train import TrainTab
from ui_modules.summarize import SummarizeTab
from ui_modules.chat import ChatTab
from ui_modules.colors import ColorsTab
from ui_modules.associations import AssociationsTab
from ui_modules.help_popup import HelpPopup
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

        # ---- Wrap content so footer can sit flush with the inside panel ----
        self.content_wrap = tk.Frame(self)
        self.content_wrap.pack(expand=1, fill="both")

        # Create tabs (Notebook is now a child of content_wrap)
        self.notebook = ttk.Notebook(self.content_wrap)
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

        # Footer links INSIDE the same panel as the Notebook (flush)
        self.create_footer_links(self.content_wrap)

        # Bind tab selection event to refresh associations when clicked
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Initialize tab modules after notebook is set up
        self.initialize_tab_modules()

    # ---------- Footer ----------
    def create_footer_links(self, parent):
        # Match notebook bg so it blends with the inside panel
        from tkinter import ttk
        bg = ttk.Style().lookup("TFrame", "background") or parent.cget("bg")

        footer = tk.Frame(parent, bg=bg)

        # Overlay in bottom-right; does NOT consume layout space
        footer.place(relx=1.0, rely=1.0, anchor="se", x=-8, y=-6)
        footer.lift()
        # keep it on top after resizes
        self.bind("<Configure>", lambda e: footer.lift())

        def make_link(text, command):
            lbl = tk.Label(footer, text=text, fg="blue", bg=bg, cursor="hand2")
            lbl.pack(side="right", padx=(0, 6))
            lbl.bind("<Button-1>", lambda e: command())

    def create_footer_links(self, parent):
        from tkinter import ttk
        bg = ttk.Style().lookup("TFrame", "background") or parent.cget("bg")

        # Full-width footer bar that overlays the bottom of the inside panel
        footer = tk.Frame(parent, bg=bg)
        footer.place(relx=0.0, rely=1.0, anchor="sw", relwidth=1.0, y=-6)  # spans left→right
        footer.lift()
        self.bind("<Configure>", lambda e: footer.lift())

        # Right-aligned container for the link labels
        right = tk.Frame(footer, bg=bg)
        right.pack(side="right", padx=8)

        def make_link(text, command):
            lbl = tk.Label(right, text=text, fg="blue", bg=bg, cursor="hand2")
            lbl.pack(side="left", padx=(0,0))
            lbl.bind("<Button-1>", lambda e: command())
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(fg="darkblue"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(fg="blue"))
            return lbl

        make_link("Help", self.open_help)
        tk.Label(right, text="|", bg=bg).pack(side="left", padx=2)
        make_link("About", self.open_about)
        tk.Label(right, text="|", bg=bg).pack(side="left", padx=2)
        make_link("Donate", self.open_donate)


    def open_help(self):
        HelpPopup(self)

    def open_about(self):
        messagebox.showinfo(
            "About MindPalette",
            "MindPalette\n\n"
            "A Python-powered tool for training, developing, and enhancing "
            "one’s understanding of synesthetic color associations."
        )

    def open_donate(self):
        webbrowser.open("https://example.com/donate")
    # ---------- /Footer ----------

    def on_tab_changed(self, event):
        current_tab = self.notebook.select()
        tab_id = self.notebook.index(current_tab)
        if tab_id == 4:  # Associations tab
            self.refresh_associations()

    def setup_cross_platform_styling(self):
        import platform
        if platform.system() == "Darwin":
            self.default_font = ("SF Pro Display", 12)
            self.small_font = ("SF Pro Display", 10)
        elif platform.system() == "Windows":
            self.default_font = ("Segoe UI", 12)
            self.small_font = ("Segoe UI", 10)
        else:
            self.default_font = ("DejaVu Sans", 12)
            self.small_font = ("DejaVu Sans", 10)

    def initialize_tab_modules(self):
        self.train_module = TrainTab(self.train_tab)
        self.summarize_module = SummarizeTab(self.summarize_tab, self.refresh_all_tabs)
        self.chat_module = ChatTab(self.chat_tab, self.refresh_all_tabs)
        self.colors_module = ColorsTab(self.view_colors_tab)
        self.associations_module = AssociationsTab(self.associations_tab, self.refresh_associations)
        set_database_update_callback(self.refresh_associations)
        self.refresh_associations()

    def refresh_all_tabs(self):
        self.summarize_module.setup_ui()
        self.chat_module.setup_ui()

    def refresh_associations(self):
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
