import tkinter as tk
from tkinter import messagebox
import os
import webbrowser
from utils import get_link_colors


class APIKeyPopup:
    def __init__(self, parent, refresh_callback=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.api_key_var = tk.StringVar()
        self.create_popup()

    def create_popup(self):
        """Create the API key popup window"""
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Add an API Key")
        self.popup.geometry("500x350")

        # Center the popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (350 // 2)
        self.popup.geometry(f"500x350+{x}+{y}")

        self.popup.transient(self.parent)
        self.popup.grab_set()
        self.popup.resizable(False, False)

        main_frame = tk.Frame(self.popup, padx=40, pady=40)
        main_frame.pack(expand=True, fill="both")

        # Title
        tk.Label(
            main_frame,
            text="Follow these simple steps to get your API key:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=(0, 25))

        # Step 1
        step1_frame = tk.Frame(main_frame)
        step1_frame.pack(anchor="w", pady=(0, 15))
        tk.Label(step1_frame, text="1. Go to ", font=("Arial", 12)).pack(side="left")
        
        # Get appropriate link colors for current system appearance
        normal_color, hover_color, _ = get_link_colors()
        
        link_label = tk.Label(step1_frame, text="this website.", font=("Arial", 12), fg=normal_color, cursor="hand2")
        link_label.pack(side="left")
        link_label.bind("<Button-1>", self.open_website)
        link_label.bind("<Enter>", lambda e: link_label.config(fg=hover_color))
        link_label.bind("<Leave>", lambda e: link_label.config(fg=normal_color))

        # Step 2
        tk.Label(
            main_frame,
            text='2. Click "Create API Key," select Gemini API, and generate a new key.',
            font=("Arial", 12), wraplength=420, justify="left"
        ).pack(anchor="w", pady=(0, 15))

        # Step 3
        tk.Label(
            main_frame,
            text="3. Copy your new API key and paste it below.",
            font=("Arial", 12)
        ).pack(anchor="w", pady=(0, 15))

        # Label + Entry in same row
        api_row = tk.Frame(main_frame)
        api_row.pack(anchor="w", pady=(0, 25), fill="x")
        tk.Label(api_row, text="Your API key:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.api_key_entry = tk.Entry(
            api_row, textvariable=self.api_key_var,
            font=("Arial", 12), width=40, show="*"
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True)

        # Centered Save button
        button_row = tk.Frame(main_frame)
        button_row.pack(fill="x")
        tk.Button(
            button_row, text="Save", command=self.save_api_key,
            font=("Arial", 12), width=12
        ).pack(anchor="center")

        self.api_key_entry.focus()
        self.popup.bind("<Return>", lambda e: self.save_api_key())

    def open_website(self, event=None):
        webbrowser.open("https://aistudio.google.com/app/apikey")

    def save_api_key(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showwarning("Invalid API Key", "Please enter an API key.")
            return

        try:
            with open(".env", "w") as f:
                f.write(f"GOOGLE_GENERATIVE_AI_API_KEY={api_key}\n")
            messagebox.showinfo("Success", "API key saved successfully!")
            self.popup.destroy()
            if self.refresh_callback:
                self.refresh_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}")
