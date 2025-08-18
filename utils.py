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


def get_color_sort_key(hex_color: str, snap_pale: bool = False):
    """
    Sort key for 12-family alternating lightness direction wheel.
    
    Band centers (degrees): [330, 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
    Corresponding to: pinks → reds → red-oranges → oranges → orange-yellows → yellows → 
                     yellow-greens → greens → blue-greens → blues → blue-violets → magentas
    
    Returns (is_grey, band_index, luminance_key, hue) where:
    - is_grey: 1 for low-saturation colors (S < 0.15), 0 for chromatic
    - band_index: 0-11 for the 12 color families
    - luminance_key: +Y for light→dark bands, -Y for dark→light bands
    - hue: for tiebreaking within bands
    """
    hue, sat, _ = hex_to_hsv(hex_color)
    lum = relative_luminance(hex_color)
    
    # Handle greys (low saturation)
    GREY_THRESHOLD = 0.15
    if sat < GREY_THRESHOLD:
        return (1, 0, lum, hue)  # greys go to the end, sorted by luminance
    
    # Optional: snap pale colors toward their band center
    if snap_pale and sat < 0.3:
        # Find nearest band center and slightly pull hue toward it
        band_centers = [330, 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
        distances = [min(abs(hue - center), abs(hue - center + 360), abs(hue - center - 360)) 
                    for center in band_centers]
        nearest_band = distances.index(min(distances))
        nearest_center = band_centers[nearest_band]
        
        # Pull hue 20% toward the band center
        hue_diff = nearest_center - hue
        if hue_diff > 180:
            hue_diff -= 360
        elif hue_diff < -180:
            hue_diff += 360
        hue = hue + 0.2 * hue_diff
        hue = hue % 360
    
    # Find nearest band center
    band_centers = [330, 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
    distances = [min(abs(hue - center), abs(hue - center + 360), abs(hue - center - 360)) 
                for center in band_centers]
    band_index = distances.index(min(distances))
    
    # Alternating lightness direction: light→dark for even bands (0,2,4...), dark→light for odd bands (1,3,5...)
    # Band 0 (pinks): light→dark, Band 1 (reds): dark→light, etc.
    if band_index % 2 == 0:
        luminance_key = lum  # light→dark
    else:
        luminance_key = -lum  # dark→light
    
    return (0, band_index, luminance_key, hue)


def sort_colors_by_rainbow(color_list, hex_key: str = 'hex', snap_pale: bool = False):
    """
    Sort a list of color dictionaries by 12-family alternating lightness direction wheel.
    
    The order flows seamlessly: all light pinks → dark pinks, all dark reds → light reds,
    all light red-oranges → dark red-oranges, all dark oranges → light oranges, etc.
    
    Parameters
    ----------
    color_list : list[dict]
        Each dict must include a hex code (default key 'hex').
    hex_key : str
        Dict key containing the hex value, e.g., '#aabbcc'.
    snap_pale : bool
        If True, slightly pull low-saturation colors toward their band center
        to prevent nearly identical "pale" hues from splitting across adjacent bands.
    
    Returns
    -------
    list[dict] : sorted copy of color_list
    """
    return sorted(
        color_list,
        key=lambda x: get_color_sort_key(x[hex_key], snap_pale=snap_pale)
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
