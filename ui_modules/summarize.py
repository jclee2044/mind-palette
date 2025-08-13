import tkinter as tk
from tkinter import messagebox, filedialog
import os
from gemini_backend import update_summary_file, has_api_key
from utils import load_database, ASCII_ART, setup_cross_platform_scrolling
from ui_modules.api_key_popup import APIKeyPopup


class SummarizeTab:
    def __init__(self, parent, refresh_all_callback=None):
        self.parent = parent
        self.refresh_all_callback = refresh_all_callback
        self.setup_ui()

    def setup_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Check if API key is available
        if not has_api_key():
            self.show_api_key_message()
            return

        summary_path = "db/summary.txt"
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read()

            # Create a container frame to center the content
            container_frame = tk.Frame(self.parent)
            container_frame.pack(expand=True, fill="both", padx=75, pady=(10, 0))
            
            # Create the text frame with constrained width
            frame = tk.Frame(container_frame)
            frame.pack(expand=True, fill="both")
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)

            # Create text widget with maximum width constraint
            text_widget = tk.Text(frame, wrap="word", width=80)  # Set a reasonable max width
            text_widget.insert("1.0", ASCII_ART + "\n" + summary_text)
            text_widget.config(state="disabled")
            text_widget.grid(row=0, column=0, sticky="nsew")

            scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            text_widget.config(yscrollcommand=scrollbar.set)
            
            # Set up cross-platform scrolling
            setup_cross_platform_scrolling(text_widget)

            # Button frame for side-by-side buttons
            button_frame = tk.Frame(container_frame)
            button_frame.pack(pady=(5, 10))
            
            update_button = tk.Button(button_frame, text="New Summary", command=self.update_summary)
            update_button.pack(side="left", padx=(0, 5))
            
            export_summary_button = tk.Button(button_frame, text="Save as .txt", command=self.export_summary)
            export_summary_button.pack(side="left", padx=(5, 0))
        else:
            tk.Label(self.parent, text="No summary found.", font=("Arial", 12)).pack(pady=20)
            generate_button = tk.Button(self.parent, text="Generate Summary", command=self.update_summary)
            generate_button.pack(pady=5)

    def show_api_key_message(self):
        """Display message when API key is missing"""
        # Create a centered container
        container = tk.Frame(self.parent)
        container.pack(expand=True, fill="both")
        
        # Center the content vertically and horizontally
        center_frame = tk.Frame(container)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Main message
        message_label = tk.Label(center_frame, text="You need an API key to use this.", 
                                font=("Arial", 14))
        message_label.pack(pady=(0, 10))
        
        # Link to add API key
        link_label = tk.Label(center_frame, text="Add one...", 
                             font=("Arial", 13), fg="blue", cursor="hand2")
        link_label.pack()
        
        # Bind click event to the link
        link_label.bind("<Button-1>", self.open_api_key_help)
        link_label.bind("<Enter>", lambda e: link_label.config(fg="darkblue"))
        link_label.bind("<Leave>", lambda e: link_label.config(fg="blue"))

    def open_api_key_help(self, event=None):
        """Open help for adding API key"""
        callback = self.refresh_all_callback if self.refresh_all_callback else self.setup_ui
        APIKeyPopup(self.parent, refresh_callback=callback)

    def update_summary(self):
        db = load_database()
        if not db:
            messagebox.showinfo("Summary", "Database is empty.")
            return

        try:
            update_summary_file(db)
            messagebox.showinfo("Summary", "Summary updated!")
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate summary: {str(e)}")

    def export_summary(self):
        summary_path = "db/summary.txt"
        if not os.path.exists(summary_path):
            messagebox.showinfo("Export", "No summary file found.")
            return

        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_text = f.read()

            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Summary"
            )

            if not file_path:
                return  # User canceled

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(ASCII_ART + summary_text)
            messagebox.showinfo("Export", f"Summary exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export summary: {str(e)}") 