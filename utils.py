import json
import os
import tkinter as tk

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
            # Check if widget still exists before trying to scroll
            if widget.winfo_exists():
                if platform.system() == "Darwin":  # macOS
                    widget.yview_scroll(int(-1 * event.delta), "units")
                else:  # Windows and Linux
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            # Widget was destroyed, ignore the error
            pass
    
    # Bind mouse wheel events to the specific widget
    widget.bind("<MouseWheel>", _on_mousewheel)
    
    # For Linux, also bind button events to the widget
    if platform.system() != "Darwin":
        widget.bind("<Button-4>", lambda e: _on_mousewheel(e) if widget.winfo_exists() else None)
        widget.bind("<Button-5>", lambda e: _on_mousewheel(e) if widget.winfo_exists() else None)
    
    # If a canvas is provided, use bind_all for the canvas to enable scrolling when hovering over frame content
    if canvas:
        # Create a canvas-specific mousewheel handler that only works when hovering over the canvas or its children
        def canvas_mousewheel(event):
            try:
                # Get the widget under the mouse cursor
                x, y = event.widget.winfo_pointerxy()
                widget_under_mouse = event.widget.winfo_containing(x, y)
                
                # Check if the mouse is over the canvas or any of its descendants
                if widget_under_mouse:
                    current = widget_under_mouse
                    while current:
                        if current == canvas:
                            # Mouse is over the canvas or its children, allow scrolling
                            _on_mousewheel(event)
                            break
                        current = current.master
            except tk.TclError:
                # Widget was destroyed, ignore the error
                pass
        
        # Use bind_all but with the canvas-specific handler
        canvas.bind_all("<MouseWheel>", canvas_mousewheel)
        
        if platform.system() != "Darwin":
            canvas.bind_all("<Button-4>", lambda e: canvas_mousewheel(e) if widget.winfo_exists() else None)
            canvas.bind_all("<Button-5>", lambda e: canvas_mousewheel(e) if widget.winfo_exists() else None) 