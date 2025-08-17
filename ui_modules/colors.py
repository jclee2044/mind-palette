import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib import colors as mcolors
from utils import load_database, save_to_database, setup_cross_platform_scrolling, load_saved_for_later, save_to_saved_for_later, remove_from_saved_for_later, sort_colors_by_rainbow


class ColorsTab:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        container = tk.Frame(self.parent)
        container.pack(pady=(60, 5))

        # --- first row: input controls ---
        entry_frame = tk.Frame(container)
        entry_frame.pack()

        tk.Label(entry_frame, text="Input Type:").pack(side="left", padx=(20, 20))
        self.input_type = ttk.Combobox(
            entry_frame,
            values=["Hex Code", "Color Name"],
            state="readonly",
            width=10
        )
        self.input_type.set("Hex Code")
        self.input_type.pack(side="left", padx=(0, 10))
        self.input_type.bind("<<ComboboxSelected>>", self.on_input_type_change)

        self.hex_entry = tk.Entry(entry_frame, width=15)
        self.hex_entry.pack(side="left")
        self.hex_entry.insert(0, "#ffffff")
        self.hex_entry.bind("<KeyRelease>", self.update_color_display)

        # --- second row: centered Browse button ---
        browse_row = tk.Frame(container)
        browse_row.pack(pady=(8, 0))  # directly below inputs, centered by default
        tk.Button(browse_row, text="Browse XKCD…", command=self.open_xkcd_browser).pack(side="left", padx=(0, 10))
        tk.Button(browse_row, text="View Saved for Later…", command=self.open_saved_later_browser).pack(side="left")

        # --- preview + labels ---
        self.color_display = tk.Canvas(
            self.parent, width=350, height=250,
            bg="#ffffff", relief="ridge", bd=2
        )
        self.color_display.pack(pady=(20, 10))

        self.color_name_label = tk.Label(self.parent, text="white", font=("Arial", 12))
        self.color_name_label.pack()

        self.hex_code_label = tk.Label(self.parent, text="#ffffff", font=("Arial", 12))
        self.hex_code_label.pack()

    def update_color_display(self, event=None):
        input_value = self.hex_entry.get().strip().lower()
        mode = self.input_type.get()

        if mode == "Hex Code":
            if input_value.startswith("#") and len(input_value) == 7:
                try:
                    self.color_display.config(bg=input_value)
                    self.hex_code_label.config(text=input_value)
                    match = [name for name, val in mcolors.XKCD_COLORS.items() if val.lower() == input_value]
                    name = match[0].replace("xkcd:", "") if match else "unknown"
                    self.color_name_label.config(text=f"{name}")
                    self.display_association(input_value)
                except tk.TclError:
                    pass

        elif mode == "Color Name":
            color_name = input_value
            hex_code = None

            if not color_name.startswith("xkcd:"):
                color_name_xkcd = "xkcd:" + color_name
            else:
                color_name_xkcd = color_name

            hex_code = mcolors.XKCD_COLORS.get(color_name_xkcd)

            if not hex_code and color_name in mcolors.CSS4_COLORS:
                hex_code = mcolors.CSS4_COLORS[color_name]

            if hex_code:
                try:
                    self.color_display.config(bg=hex_code)
                    self.hex_code_label.config(text=hex_code)
                    display_name = color_name.replace("xkcd:", "")
                    self.color_name_label.config(text=f"{display_name}")
                    self.display_association(hex_code)
                except tk.TclError:
                    pass

    def on_input_type_change(self, event=None):
        current_hex = self.color_display["bg"].lower()

        if self.input_type.get() == "Color Name":
            match = [name for name, val in mcolors.XKCD_COLORS.items() if val.lower() == current_hex]
            color_name = match[0].replace("xkcd:", "") if match else "unknown"
            self.hex_entry.delete(0, tk.END)
            self.hex_entry.insert(0, color_name)
        else:
            self.hex_entry.delete(0, tk.END)
            self.hex_entry.insert(0, current_hex)

    def display_association(self, hex_code):
        db = load_database()
        association = None
        for entry in db:
            if entry["hex"].lower() == hex_code.lower():
                association = entry["associations"]
                break

        if association:
            # Create a popup to show the association
            popup = tk.Toplevel(self.parent)
            popup.title("Color Association")
            popup.geometry("400x200")
            popup.transient(self.parent)
            popup.grab_set()

            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (400 // 2)
            y = (popup.winfo_screenheight() // 2) - (200 // 2)
            popup.geometry(f"400x200+{x}+{y}")

            # Content
            tk.Label(popup, text=f"Association for {hex_code}:", font=("Arial", 12, "bold")).pack(pady=10)
            text_widget = tk.Text(popup, wrap="word", height=6, width=50)
            text_widget.pack(padx=20, pady=10, fill="both", expand=True)
            text_widget.insert("1.0", association)
            text_widget.config(state="disabled")

            # Close button
            tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

    def open_xkcd_browser(self):
        # Create popup window
        win = tk.Toplevel(self.parent)
        win.title("Browse XKCD Colors")
        win.geometry("300x350")
        win.transient(self.parent)
        win.grab_set()

        # Center the popup
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (300 // 2)
        y = (win.winfo_screenheight() // 2) - (350 // 2)
        win.geometry(f"300x350+{x}+{y}")

        # Search frame
        top = tk.Frame(win)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="Search:", font=("Arial", 11, "bold")).pack(side="left")
        query_var = tk.StringVar()
        query_entry = tk.Entry(top, textvariable=query_var, width=30)
        query_entry.pack(side="left", padx=(5, 0))

        # Scrollable frame for colors
        canvas = tk.Canvas(win)
        vsb = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        rows_frame = tk.Frame(canvas)

        rows_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Cross‑platform scrolling
        setup_cross_platform_scrolling(canvas, rows_frame)

        # === NEW/UPDATED: sets for association + saved-for-later ===
        db = load_database()
        has_assoc_hex = {e["hex"].lower() for e in db if e.get("associations", "").strip()}
        saved_hex = {e["hex"].lower() for e in load_saved_for_later()}

        # === CHANGED: include has_assoc and is_saved flags in each row dict ===
        all_rows = [{"name": n.replace("xkcd:", ""), "hex": hx,
                    "has_assoc": (hx.lower() in has_assoc_hex),
                    "is_saved": (hx.lower() in saved_hex)}
                    for n, hx in mcolors.XKCD_COLORS.items()]
        
        # Sort by true rainbow order using the new function
        all_rows = sort_colors_by_rainbow(all_rows)

        # --- header ---
        hdr = tk.Frame(rows_frame)
        hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="Color", font=("Arial", 10, "bold"), width=6).pack(side="left", padx=(0, 4))
        tk.Label(hdr, text="Name", font=("Arial", 10, "bold"), width=16, anchor="w").pack(side="left")
        tk.Label(hdr, text="Hex", font=("Arial", 10, "bold"), width=10, anchor="w").pack(side="left", padx=(0))
        # === NEW: Status column header ===
        tk.Label(hdr, text="Status", font=("Arial", 10, "bold"), width=7, anchor="w").pack(side="left", padx=(6, 0))
        ttk.Separator(rows_frame, orient="horizontal").pack(fill="x", pady=(0, 4))

        # --- selection handler -> fills Colors tab ---
        def choose(hx, nm):
            self.input_type.set("Hex Code")
            self.hex_entry.delete(0, tk.END)
            self.hex_entry.insert(0, hx)
            self.update_color_display()
            win.destroy()

        # --- table populate/filter ---
        row_widgets = []
        def populate(data):
            for w in row_widgets:
                w.destroy()
            row_widgets.clear()

            for e in data:
                rf = tk.Frame(rows_frame)
                rf.pack(fill="x", pady=0)

                tk.Canvas(rf, width=20, height=20, bg=e["hex"], relief="solid", bd=1).pack(side="left", padx=(0, 4))
                tk.Label(rf, text=e["name"], width=12, anchor="w").pack(side="left")
                tk.Label(rf, text=e["hex"], width=7, anchor="w").pack(side="left", padx=(3, 0))

                # === NEW: status indicators (✓ if association exists, S if saved for later) ===
                status_text = ""
                status_color = "black"
                status_font = ("Arial", 17, "bold")  # default for ✓
                if e.get("has_assoc"):
                    status_text = "✓"
                    status_color = "green"
                elif e.get("is_saved"):
                    status_text = "S"
                    status_color = "#3d7afd"
                    status_font = ("Arial", 16)

                tk.Label(
                    rf,
                    text=status_text,
                    width=7,
                    anchor="w",
                    fg=status_color,
                    font=status_font
                ).pack(side="left", padx=(6, 0))

                def _on_click(ev=None, hx=e["hex"], nm=e["name"]):
                    choose(hx, nm)
                rf.bind("<Button-1>", _on_click)
                for c in rf.winfo_children():
                    c.bind("<Button-1>", _on_click)

                row_widgets.append(rf)

        def do_filter(*_):
            q = query_var.get().strip().lower()
            if not q:
                populate(all_rows)
            else:
                filtered = [e for e in all_rows if q in e["name"].lower() or q in e["hex"].lower()]
                populate(filtered)

        query_var.trace("w", do_filter)
        populate(all_rows)

    def add_association_popup(self, hex_code):
        # Popup window
        popup = tk.Toplevel(self.parent)
        popup.title("Add Association")
        popup.geometry("400x175")
        popup.transient(self.parent)
        popup.grab_set()

        # Center the popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 125 + 150
        popup.geometry(f"400x175+{x}+{y}")

        # Color name lookup
        xkcd_name = [name.replace("xkcd:", "") for name, val in mcolors.XKCD_COLORS.items() if val == hex_code]
        name = xkcd_name[0] if xkcd_name else "unknown"

        # Header
        tk.Label(popup, text=f"{name} ({hex_code})", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        # Entry field
        text = tk.Text(popup, height=5, wrap="word")
        text.pack(padx=15, pady=(0, 10), fill="both", expand=True)

        # Buttons
        def save_and_close():
            assoc = text.get("1.0", tk.END).strip()
            if assoc:
                entry = {
                    "hex": hex_code,
                    "xkcd_name": name,
                    "associations": assoc
                }
                save_to_database(entry)
                # Remove from saved_for_later if it was there
                remove_from_saved_for_later(hex_code)
                popup.destroy()
                self.update_color_display()  # Refresh the displayed association
            else:
                messagebox.showerror("Error", "Association cannot be empty.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Save", command=save_and_close).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5)

    def save_current_for_later(self, hex_code):
        """Save the current color for later without writing an association"""
        xkcd_name = [name.replace("xkcd:", "") for name, val in mcolors.XKCD_COLORS.items() if val == hex_code]
        name = xkcd_name[0] if xkcd_name else "unknown"
        
        entry = {
            "hex": hex_code,
            "xkcd_name": name
        }
        save_to_saved_for_later(entry)
        
        # Create a custom messagebox positioned lower on screen
        msg_win = tk.Toplevel(self.parent)
        msg_win.title("Saved")
        msg_win.geometry("300x100")
        msg_win.transient(self.parent)
        msg_win.grab_set()
        
        # Position lower on screen
        msg_win.update_idletasks()
        x = (msg_win.winfo_screenwidth() // 2) - 150
        y = (msg_win.winfo_screenheight() // 2) + 100  # Lower position
        msg_win.geometry(f"300x100+{x}+{y}")
        
        tk.Label(msg_win, text=f"'{name}' has been saved for later!", font=("Arial", 11)).pack(expand=True)
        tk.Button(msg_win, text="OK", command=msg_win.destroy).pack(pady=10)
        
        # Auto-close after 2 seconds
        msg_win.after(2000, msg_win.destroy) 

    def open_saved_later_browser(self):
        saved_colors = load_saved_for_later()
        if not saved_colors:
            messagebox.showinfo("No Saved Colors", "You have no colors saved for later.")
            return

        win = tk.Toplevel(self.parent)
        win.title(f"Saved for Later ({len(saved_colors)})")
        win.geometry("260x350")
        win.transient(self.parent)
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 150
        y = (win.winfo_screenheight() // 2) - 200 + 80
        win.geometry(f"260x350+{x}+{y}")

        # --- search bar ---
        top = tk.Frame(win)
        top.pack(fill="x", padx=10, pady=(10, 6))
        tk.Label(top, text="Search:", font=("Arial", 11)).pack(side="left")
        query_var = tk.StringVar()
        search_entry = tk.Entry(top, textvariable=query_var, width=25)
        search_entry.pack(side="left", padx=(8, 0))
        search_entry.focus_set()

        instr = tk.Label(
            win,
            text="Click any color to load it in the viewer.",
            font=("Arial", 11, "italic"),
            fg="gray",
            anchor="w",
            justify="left"
        )
        instr.pack(pady=(0, 4))

        # --- scrollable table area ---
        table_wrap = tk.Frame(win)
        table_wrap.pack(fill="both", expand=True, pady=(0))

        canvas = tk.Canvas(table_wrap, highlightthickness=0)
        vsb = ttk.Scrollbar(table_wrap, orient="vertical", command=canvas.yview)
        rows_frame = tk.Frame(canvas)
        rows_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # Set up cross-platform scrolling for the saved colors browser
        setup_cross_platform_scrolling(canvas, rows_frame)

        # --- data prep (name, hex) ---
        all_rows = [{"name": c["xkcd_name"].replace("xkcd:", ""), "hex": c["hex"]} for c in saved_colors]
        # Sort by true rainbow order using the new function
        all_rows = sort_colors_by_rainbow(all_rows)

        # --- header ---
        hdr = tk.Frame(rows_frame)
        hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text="Color", font=("Arial", 10, "bold"), width=6).pack(side="left", padx=(0, 4))
        tk.Label(hdr, text="Name", font=("Arial", 10, "bold"), width=16, anchor="w").pack(side="left")
        tk.Label(hdr, text="Hex", font=("Arial", 10, "bold"), width=10, anchor="w").pack(side="left", padx=(0))
        tk.Label(hdr, text="", font=("Arial", 10, "bold"), width=3, anchor="w").pack(side="left", padx=(6, 0))
        ttk.Separator(rows_frame, orient="horizontal").pack(fill="x", pady=(0, 4))

        # --- selection handler -> loads color in viewer (same as XKCD browser) ---
        def choose(hx, nm):
            # Jump to Colors tab, set to Hex mode, set hex, update preview
            self.input_type.set("Hex Code")
            self.hex_entry.delete(0, tk.END)
            self.hex_entry.insert(0, hx)
            self.update_color_display()
            win.destroy()

        # --- table populate/filter ---
        row_widgets = []
        def populate(data):
            # clear previous rows
            for w in row_widgets:
                w.destroy()
            row_widgets.clear()

            for e in data:
                rf = tk.Frame(rows_frame)
                rf.pack(fill="x", pady=0)

                tk.Canvas(rf, width=20, height=20, bg=e["hex"], relief="solid", bd=1).pack(side="left", padx=(0, 4))
                tk.Label(rf, text=e["name"], width=12, anchor="w").pack(side="left")
                tk.Label(rf, text=e["hex"], width=7, anchor="w").pack(side="left", padx=(3, 0))

                # Delete button
                def delete_color(ev=None, hx=e["hex"]):
                    remove_from_saved_for_later(hx)
                    win.destroy()
                    self.open_saved_later_browser()  # Re-open to show updated list
                
                delete_btn = tk.Label(rf, text="×", font=("Arial", 13, "bold"), fg="grey", width=3)
                delete_btn.pack(side="left", padx=(6, 0))
                delete_btn.bind("<Button-1>", delete_color)

                # click/enter selects (but not on delete button)
                def _on_click(ev=None, hx=e["hex"], nm=e["name"]):
                    choose(hx, nm)
                rf.bind("<Button-1>", _on_click)
                for c in rf.winfo_children():
                    if c != delete_btn:  # Don't bind delete button to choose function
                        c.bind("<Button-1>", _on_click)

                row_widgets.append(rf)

        def do_filter(*_):
            q = query_var.get().strip().lower()
            if not q:
                populate(all_rows)
            else:
                filtered = [e for e in all_rows if q in e["name"].lower() or q in e["hex"].lower()]
                populate(filtered)

        query_var.trace("w", do_filter)
        populate(all_rows)

        # keyboard niceties: Enter picks first visible, Esc closes
        def pick_first(_=None):
            if row_widgets:
                row_widgets[0].event_generate("<Button-1>")
        win.bind("<Return>", pick_first)
        win.bind("<Escape>", lambda e: win.destroy()) 