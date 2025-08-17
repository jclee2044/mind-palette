import json
import os
import tkinter as tk
import colorsys

# Global callback for database updates
_database_update_callback = None

def set_database_update_callback(callback):
    """Set a callback function to be called when the database is updated"""
    global _database_update_callback
    _database_update_callback = callback

def get_database_update_callback():
    """Get the current database update callback"""
    return _database_update_callback

# Database paths
DB_PATH = "db/associations.json"
saved_for_later_PATH = "db/saved_for_later.json"


# ---------- Color utilities ----------

def relative_luminance(hex_color: str) -> float:
    """
    Compute perceptual lightness Y from linearized sRGB.
    Returns a value in [0, 1].
    """
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0

    def to_linear(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    R, G, B = map(to_linear, (r, g, b))
    # Relative luminance per ITU-R BT.709
    return 0.2126 * R + 0.7152 * G + 0.0722 * B


def hex_to_hsv(hex_color):
    """
    Convert hex color to HSV values.
    Returns (hue, saturation, value) where hue is 0-360 degrees.
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360.0, s, v


def get_color_sort_key(
    hex_color: str,
    order: str = "dark_to_light",
    hue_bucket_deg: int = 12,
    zigzag: bool = True,   # <-- default: alternate per hue bucket
):
    """
    Sort key for rainbow order with alternating luminance direction per hue bucket.

    Key shape:
        (is_grey, hue_bucket, luminance_key, hue_tiebreak)

    - Low-saturation colors ("greys") are sent to the end and sorted by luminance.
    - Chromatic colors are bucketed by hue (size=hue_bucket_deg).
    - Within a bucket, we order by perceptual luminance (relative_luminance).
    - If zigzag=True (default), odd-numbered buckets flip the luminance direction so
      families alternate dark→light, light→dark, dark→light, ...
    """
    hue, sat, _ = hex_to_hsv(hex_color)
    lum = relative_luminance(hex_color)

    GREY_THRESHOLD = 0.15
    if sat < GREY_THRESHOLD:
        lum_key = lum if order == "dark_to_light" else -lum
        return (1, 0, lum_key, hue)  # greys go after chromatic colors

    total_buckets = max(1, int(360 // hue_bucket_deg))
    bucket = int(hue // hue_bucket_deg) % total_buckets

    # Base luminance direction
    lum_key = lum if order == "dark_to_light" else -lum

    # Zig-zag: flip on odd buckets (bucket 0 = reds = dark→light)
    if zigzag and (bucket % 2 == 1):
        lum_key = -lum_key

    return (0, bucket, lum_key, hue)


def sort_colors_by_rainbow(
    color_list,
    hex_key: str = 'hex',
    order: str = "dark_to_light",
    hue_bucket_deg: int = 12,
    zigzag: bool = True,   # <-- default on so UI gets seamless blending automatically
):
    """
    Sort a list of color dictionaries by rainbow order with alternating
    dark↔light progression across hue families (zig-zag by default).

    Parameters
    ----------
    color_list : list[dict]
        Each dict must include a hex code (default key 'hex').
    hex_key : str
        Dict key containing the hex value, e.g., '#aabbcc'.
    order : {'dark_to_light', 'light_to_dark'}
        Baseline direction. With zigzag=True, odd buckets are flipped.
    hue_bucket_deg : int
        Bucket size for grouping by hue (e.g., 12 -> 30 buckets).
    zigzag : bool
        If True, alternate luminance direction per bucket for seamless handoffs.

    Returns
    -------
    list[dict] : sorted copy of color_list
    """
    return sorted(
        color_list,
        key=lambda x: get_color_sort_key(
            x[hex_key],
            order=order,
            hue_bucket_deg=hue_bucket_deg,
            zigzag=zigzag,
        ),
    )


# ---------- Database helpers ----------

def load_database():
    """Load the associations database from JSON file"""
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            return []
    elif os.path.exists("db/associations_backup.json"):
        try:
            with open("db/associations_backup.json", "r") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            return []
    return []


def save_to_database(entry):
    """Save an entry to the associations database"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = load_database()
    if not any(d["hex"] == entry["hex"] for d in db):
        db.append(entry)
        with open(DB_PATH, "w") as f:
            json.dump(db, f, indent=4)

        with open("db/associations_backup.json", "w") as f:
            json.dump(db, f, indent=4)

        # Trigger the callback if it exists
        callback = get_database_update_callback()
        if callback:
            callback()


def load_saved_for_later():
    """Load the save for later database from JSON file"""
    if os.path.exists(saved_for_later_PATH):
        try:
            with open(saved_for_later_PATH, "r") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            return []
    return []


def save_to_saved_for_later(entry):
    """Save an entry to the save for later database"""
    os.makedirs(os.path.dirname(saved_for_later_PATH), exist_ok=True)
    db = load_saved_for_later()
    if not any(d["hex"] == entry["hex"] for d in db):
        db.append(entry)
        with open(saved_for_later_PATH, "w") as f:
            json.dump(db, f, indent=4)


def remove_from_saved_for_later(hex_code):
    """Remove an entry from the save for later database"""
    db = load_saved_for_later()
    db = [entry for entry in db if entry["hex"] != hex_code]
    with open(saved_for_later_PATH, "w") as f:
        json.dump(db, f, indent=4)


# ---------- UI helpers ----------

# ASCII Art constant
ASCII_ART = r""" __  __                ____                  __  __           _     
 \ \/ /__  __ ______  / __/_ _____  ___ ___ / /_/ /  ___ ___ (_)__ _
  \  / _ \/ // / __/ _\ \/ // / _ \/ -_|_-</ __/ _ \/ -_|_-</ / _ `/
  /_/\___/\_,_/_/   /___/\_, /_//_/\__/___/\__/_/__/\__/___/_/\_,_/ 
                        /___/ 
"""


def setup_cross_platform_scrolling(widget, canvas=None):
    """Set up cross-platform mouse wheel scrolling for a widget"""
    import platform
    
    def _on_mousewheel(event):
        try:
            if widget.winfo_exists():
                if platform.system() == "Darwin":  # macOS
                    widget.yview_scroll(int(-1 * event.delta), "units")
                else:  # Windows and Linux
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass
    
    # Bind mouse wheel events to the specific widget
    widget.bind("<MouseWheel>", _on_mousewheel)
    
    # For Linux, also bind button events to the widget
    if platform.system() != "Darwin":
        widget.bind("<Button-4>", lambda e: _on_mousewheel(e) if widget.winfo_exists() else None)
        widget.bind("<Button-5>", lambda e: _on_mousewheel(e) if widget.winfo_exists() else None)
    
    # If a canvas is provided, enable scrolling when hovering over frame content
    if canvas:
        def canvas_mousewheel(event):
            try:
                x, y = event.widget.winfo_pointerxy()
                widget_under_mouse = event.widget.winfo_containing(x, y)
                if widget_under_mouse:
                    current = widget_under_mouse
                    while current:
                        if current == canvas:
                            _on_mousewheel(event)
                            break
                        current = current.master
            except tk.TclError:
                pass
        
        canvas.bind_all("<MouseWheel>", canvas_mousewheel)
        if platform.system() != "Darwin":
            canvas.bind_all("<Button-4>", lambda e: canvas_mousewheel(e) if widget.winfo_exists() else None)
            canvas.bind_all("<Button-5>", lambda e: canvas_mousewheel(e) if widget.winfo_exists() else None)
