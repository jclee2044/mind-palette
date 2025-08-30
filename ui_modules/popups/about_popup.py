import tkinter as tk
from tkinter import ttk
import os


class AboutPopup:
    def __init__(self, parent):
        self.parent = parent
        self.create_popup()

    def create_popup(self):
        """Create the about popup window"""
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("About")
        self.popup.geometry("700x500")
        
        # Center the popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (500 // 2)
        self.popup.geometry(f"700x500+{x}+{y}")
        
        self.popup.transient(self.parent)
        self.popup.grab_set()
        self.popup.resizable(False, False)
        
        # Main container
        main_container = tk.Frame(self.popup, padx=30, pady=25)
        main_container.pack(expand=True, fill="both")
        
        # Create the two sections
        self.create_mindpalette_section(main_container)
        self.create_developer_section(main_container)

    def create_mindpalette_section(self, parent):
        """Create the About MindPalette section"""
        # Section title
        title_label = tk.Label(
            parent, 
            text="About MindPalette", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(anchor="center")
        
        # Content frame with two columns
        content_frame = tk.Frame(parent)
        content_frame.pack(fill="x", pady=(0, 5))
        
        # Left column - Image
        image_frame = tk.Frame(content_frame, width=110, height=110)
        image_frame.pack(side="left", padx=(20, 20))
        image_frame.pack_propagate(False)
        
        # Try to load the app icon
        try:
            icon_path = "icons/app_icon_no_border_w_shadow_padded_new_final.png"
            if os.path.exists(icon_path):
                # Load and resize the image maintaining aspect ratio
                from PIL import Image, ImageTk
                original_image = Image.open(icon_path)
                # Calculate aspect ratio to maintain proportions
                width, height = original_image.size
                aspect_ratio = width / height
                if aspect_ratio > 1:  # wider than tall
                    new_width = 130
                    new_height = int(130 / aspect_ratio)
                else:  # taller than wide
                    new_height = 130
                    new_width = int(130 * aspect_ratio)
                resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                icon_image = ImageTk.PhotoImage(resized_image)
                icon_label = tk.Label(image_frame, image=icon_image)
                icon_label.image = icon_image  # Keep a reference
                icon_label.pack(expand=True)
            else:
                # Fallback placeholder
                placeholder = tk.Label(
                    image_frame, 
                    text="🎨", 
                    font=("Arial", 32),
                    bg="#f0f0f0",
                    relief="solid",
                    bd=1
                )
                placeholder.pack(expand=True)
        except Exception as e:
            # Fallback placeholder
            placeholder = tk.Label(
                image_frame, 
                text="🎨", 
                font=("Arial", 32),
                bg="#f0f0f0",
                relief="solid",
                bd=1
            )
            placeholder.pack(expand=True)
        
        # Right column - Text
        text_frame = tk.Frame(content_frame)
        text_frame.pack(side="left", fill="both", expand=True)
        
        mindpalette_text = (
            "For synesthetes, the feeling is all too familiar. You're trying to describe "
            "what you see, and you just can't find the words— or the color— to do it justice. "
            "That's where MindPalette comes in.\n\n"
            "This new and exciting app allows you to actively sharpen your senses and "
            "strengthen your perceptions, while perfectly matching your associations with "
            "the colors they represent. Now, when someone asks you what color something is, "
            "you can show them the exact same shade that's in your brain.\n\n"
            "And not only that, but you can summarize and chat with your data to learn "
            "more about your synesthesia, or share your associations with others. In short, "
            "this is your personal journal summarization powerhouse for all things synesthesia. "
            "So, make it your own and be proud of it."
        )
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            font=("Arial", 13),
            height=13,
            padx=10,
            pady=10,
            relief="flat",
            bg=text_frame.cget("bg"),
            state="disabled"
        )
        text_widget.pack(fill="both", expand=True)
        
        # Insert text
        text_widget.config(state="normal")
        text_widget.insert("1.0", mindpalette_text)
        text_widget.config(state="disabled")



    def create_developer_section(self, parent):
        """Create the About the developer section"""
        # Section title
        title_label = tk.Label(
            parent, 
            text="About the developer", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(anchor="center", pady=(5, 0))
        
        # Content frame with two columns
        content_frame = tk.Frame(parent)
        content_frame.pack(fill="x")
        
        # Left column - Image
        image_frame = tk.Frame(content_frame, width=120, height=130)
        image_frame.pack(side="left", padx=(20, 10))
        image_frame.pack_propagate(False)
        
        # Try to load the developer image
        try:
            dev_image_path = "ui_modules/popups/developer.png"
            if os.path.exists(dev_image_path):
                # Load and resize the image maintaining aspect ratio
                from PIL import Image, ImageTk
                original_image = Image.open(dev_image_path)
                # Calculate aspect ratio to maintain proportions
                width, height = original_image.size
                aspect_ratio = width / height
                if aspect_ratio > 1:  # wider than tall
                    new_width = 120
                    new_height = int(130 / aspect_ratio)
                else:  # taller than wide
                    new_height = 130
                    new_width = int(130 * aspect_ratio)
                resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                dev_image = ImageTk.PhotoImage(resized_image)
                dev_label = tk.Label(image_frame, image=dev_image)
                dev_label.image = dev_image  # Keep a reference
                dev_label.pack(expand=True)
            else:
                # Fallback placeholder
                placeholder = tk.Label(
                    image_frame, 
                    text="👨‍💻", 
                    font=("Arial", 32),
                    bg="#f0f0f0",
                    relief="solid",
                    bd=1
                )
                placeholder.pack(expand=True)
        except Exception as e:
            # Fallback placeholder
            placeholder = tk.Label(
                image_frame, 
                text="👨‍💻", 
                font=("Arial", 32),
                bg="#f0f0f0",
                relief="solid",
                bd=1
            )
            placeholder.pack(expand=True)
        
        # Right column - Text
        text_frame = tk.Frame(content_frame)
        text_frame.pack(side="left", fill="both", expand=True)
        
        developer_text = (
            "Hi, synesthetes! My name is Jacob Lee; I am a Human-Centered Design and "
            "Development student at Penn State University, focused on building custom AI "
            "tools for automation and personal development.\n\n"
            "This is the first full-fledged project that I've built from scratch, which "
            "is one more reason why I am so excited to share it with you.\n\n"
            "Please feel free to reach out to me at jclee2044@gmail.com with any thoughts, "
            "ideas, or requests. I would love to hear from you!"
        )
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            font=("Arial", 13),
            height=13,
            padx=10,
            pady=10,
            relief="flat",
            bg=text_frame.cget("bg"),
            state="disabled"
        )
        text_widget.pack(fill="both", expand=True)
        
        # Insert text
        text_widget.config(state="normal")
        text_widget.insert("1.0", developer_text)
        text_widget.config(state="disabled") 