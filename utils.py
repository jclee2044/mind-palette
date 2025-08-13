import json
import os


# Database path
DB_PATH = "db/associations.json"


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
        if platform.system() == "Darwin":  # macOS
            widget.yview_scroll(int(-1 * event.delta), "units")
        else:  # Windows and Linux
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # Bind mouse wheel events
    widget.bind_all("<MouseWheel>", _on_mousewheel)
    
    # For Linux, also bind button events
    if platform.system() != "Darwin":
        widget.bind_all("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))
        widget.bind_all("<Button-5>", lambda e: widget.yview_scroll(1, "units"))
    
    # If a canvas is provided, also bind to it for better coverage
    if canvas:
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        if platform.system() != "Darwin":
            canvas.bind_all("<Button-4>", lambda e: widget.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: widget.yview_scroll(1, "units")) 