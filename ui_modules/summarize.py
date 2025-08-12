import tkinter as tk
from tkinter import messagebox, filedialog
import os
from gemini_backend import update_summary_file
from utils import load_database, ASCII_ART


class SummarizeTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

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