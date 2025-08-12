import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib import colors as mcolors
from utils import load_database, save_to_database


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
        tk.Button(browse_row, text="Browse XKCD…", command=self.open_xkcd_browser).pack()

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

        elif self.input_type.get() == "Hex Code":
            self.hex_entry.delete(0, tk.END)
            self.hex_entry.insert(0, current_hex)

        self.update_color_display()

    def open_xkcd_browser(self):
        # --- popup scaffold ---
        win = tk.Toplevel(self.parent)
        win.title("Browse XKCD Colors")
        win.geometry("300x350")
        win.transient(self.parent)
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 150
        y = (win.winfo_screenheight() // 2) - 200 + 80
        win.geometry(f"300x350+{x}+{y}")

        # --- search bar ---
        top = tk.Frame(win)
        top.pack(fill="x", padx=10, pady=(10, 6))
        tk.Label(top, text="Search:", font=("Arial", 11, "bold")).pack(side="left")
        query_var = tk.StringVar()
        search_entry = tk.Entry(top, textvariable=query_var, width=35)
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

        # === NEW: build a set of hex codes that have associations ===
        db = load_database()
        has_assoc_hex = {e["hex"].lower() for e in db if e.get("associations", "").strip()}

        # --- data prep (name, hex), rainbow-ish sort for nicer browsing ---
        rainbow_order = {'pink':0,'red':1,'orang':2,'yellow':3,'gold':3,'green':4,'teal':5,
                        'turquoise':5,'cyan':5,'blue':6,'indigo':7,'violet':8,'periwinkle':8,'purple':9}
        def pri(name):
            l = name.lower()
            for k,v in rainbow_order.items():
                if k in l: return v
            return 999

        # === CHANGED: include has_assoc flag in each row dict ===
        all_rows = [{"name": n.replace("xkcd:", ""), "hex": hx, "has_assoc": (hx.lower() in has_assoc_hex)}
                    for n, hx in mcolors.XKCD_COLORS.items()]
        all_rows.sort(key=lambda d: (pri(d["name"]), d["name"]))

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

                # === NEW: status checkmark (✓ if association exists) ===
                status_text = "✓" if e.get("has_assoc") else ""
                tk.Label(
                    rf,
                    text=status_text,
                    width=7,
                    anchor="w",
                    fg="green",
                    font=("Arial", 17, "bold")  # bigger and bold
                ).pack(side="left", padx=(6, 0))

                # click/enter selects
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
                # === CHANGED: keep has_assoc in filtered data ===
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

    def display_association(self, hex_code):
        db = load_database()
        match = next((entry for entry in db if entry["hex"].lower() == hex_code.lower()), None)

        if not hasattr(self, "association_label"):
            self.association_label = tk.Label(
                self.parent,
                text="",
                wraplength=300,
                font=("Arial", 10),
                fg="gray"
            )
            self.association_label.pack(pady=(15, 0))

        if not hasattr(self, "write_one_link"):
            self.write_one_link = tk.Label(
                self.parent,
                text="Write one...",
                font=("Arial", 10),
                fg="blue",
                cursor="hand2"
            )
            self.write_one_link.bind("<Button-1>", lambda e: self.add_association_popup(hex_code))
            self.write_one_link.pack(pady=(0, 10))
        else:
            self.write_one_link.bind("<Button-1>", lambda e: self.add_association_popup(hex_code))

        if match and match.get("associations"):
            self.association_label.config(text=match["associations"])
            self.write_one_link.pack_forget()  # Hide "Write one..." if an association exists
        else:
            self.association_label.config(text="No associations described yet.")
            self.write_one_link.pack()  # Show "Write one..."

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
                popup.destroy()
                self.update_color_display()  # Refresh the displayed association
            else:
                messagebox.showerror("Error", "Association cannot be empty.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Save", command=save_and_close).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5) 