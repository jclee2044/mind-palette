import tkinter as tk
from tkinter import messagebox
import random
from matplotlib import colors as mcolors
from key_bindings import apply_text_navigation_bindings, bind_enter_to_submit
from utils import load_database, save_to_database, save_to_saved_for_later, remove_from_saved_for_later

# Generate color list from XKCD
XKCD_COLORS = list(mcolors.XKCD_COLORS.values())


class TrainTab:
    def __init__(self, parent):
        self.parent = parent
        self.current_color = "#ffffff"  # placeholder so widgets render
        self.setup_ui()

    def setup_ui(self):
        # Create main container frame
        main_frame = tk.Frame(self.parent)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create top spacer frame
        top_spacer = tk.Frame(main_frame)
        top_spacer.pack(expand=True, fill="both")
        
        # Create content frame
        content_frame = tk.Frame(main_frame)
        content_frame.pack()
        
        # Create bottom spacer frame
        bottom_spacer = tk.Frame(main_frame)
        bottom_spacer.pack(expand=True, fill="both")
        
        # Color display section
        self.color_canvas = tk.Canvas(content_frame, width=350, height=250, bg=self.current_color)
        self.color_canvas.pack(pady=(0, 5))
        self.hex_label = tk.Label(content_frame, text=self.current_color, font=("Arial", 12))
        self.hex_label.pack(pady=(0, 10))

        # Input section
        tk.Label(content_frame, text="Synesthetic Association(s):").pack(pady=(0, 5))
        self.synesth_entry = tk.Text(content_frame, height=4, width=60, wrap="word")
        self.synesth_entry.pack(pady=(0, 10))
        bind_enter_to_submit(self.synesth_entry, self.next_color)
        apply_text_navigation_bindings(self.synesth_entry)

        # Button section
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=(0, 10))
        self.next_button = tk.Button(button_frame, text="Skip/Next Color", command=self.next_color)
        self.next_button.pack(side="left", padx=(0, 10))
        self.save_later_button = tk.Button(button_frame, text="Save for Later", command=self.saved_for_later)
        self.save_later_button.pack(side="left")

        # Bottom section with count (outside the centered content)
        self.color_count_label = tk.Label(self.parent, text=f"Colors described: {len(load_database())}")
        self.color_count_label.pack(side="bottom", pady=(0, 10))

        # Immediately load an untrained color
        self.next_color()

    def next_color(self):
        assoc = self.synesth_entry.get("1.0", tk.END).strip()

        # Save current if user wrote something
        if assoc:
            hex_code = self.current_color
            xkcd_name = [name.replace("xkcd:", "") for name, hx in mcolors.XKCD_COLORS.items() if hx == hex_code]
            entry = {
                "hex": hex_code,
                "xkcd_name": xkcd_name[0] if xkcd_name else "unknown",
                "associations": assoc
            }
            save_to_database(entry)
            # Remove from saved_for_later if it was there
            remove_from_saved_for_later(hex_code)

        # Filter to only colors with NO association yet
        db = load_database()
        used = {e["hex"].lower() for e in db}
        candidates = [c for c in XKCD_COLORS if c.lower() not in used]

        if not candidates:
            messagebox.showinfo("Done", "All colors have been described!")
            return

        # Pick and display next untrained color
        self.current_color = random.choice(candidates)
        self.color_canvas.config(bg=self.current_color)
        self.hex_label.config(text=self.current_color)
        self.synesth_entry.delete("1.0", tk.END)
        self.color_count_label.config(text=f"Colors described: {len(db)}") 

    def saved_for_later(self):
        """Save the current color for later without writing an association"""
        hex_code = self.current_color
        xkcd_name = [name.replace("xkcd:", "") for name, hx in mcolors.XKCD_COLORS.items() if hx == hex_code]
        entry = {
            "hex": hex_code,
            "xkcd_name": xkcd_name[0] if xkcd_name else "unknown"
        }
        save_to_saved_for_later(entry)
        self.next_color() 