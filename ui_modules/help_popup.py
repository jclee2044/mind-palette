import tkinter as tk
from tkinter import ttk
import os


class HelpPopup:
    def __init__(self, parent):
        self.parent = parent
        self.sections = []
        self.current_section = 0
        self.create_popup()

    def create_popup(self):
        """Create the help popup window with sidebar navigation"""
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Help Menu")
        self.popup.geometry("675x550")
        
        # Center the popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (675 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (550 // 2)
        self.popup.geometry(f"675x550+{x}+{y}")
        
        self.popup.transient(self.parent)
        self.popup.grab_set()
        self.popup.resizable(True, True)
        
        # Main container
        main_container = tk.Frame(self.popup)
        main_container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create sidebar and content area
        self.create_sidebar(main_container)
        self.create_content_area(main_container)
        
        # Load help content
        self.load_help_content()

    def create_sidebar(self, parent):
        """Create the sidebar with section navigation"""
        # Sidebar frame
        sidebar_frame = tk.Frame(parent, width=220, relief="groove", bd=1)
        sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # Sidebar title
        title_label = tk.Label(sidebar_frame, text="Sections", font=("Arial", 14, "bold"))
        title_label.pack(pady=(15, 15))
        
        # Create a canvas and scrollbar for the sections
        canvas = tk.Canvas(sidebar_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(sidebar_frame, orient="vertical", command=canvas.yview, width=0)
        
        # Create a frame for the section buttons inside the canvas
        self.sections_frame = tk.Frame(canvas)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=(10,10))
        
        # Create a window in the canvas for the sections frame
        canvas.create_window((0, 0), window=self.sections_frame, anchor="nw")
        
        # Configure the sections frame to expand
        self.sections_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def create_content_area(self, parent):
        """Create the main content area with text display"""
        # Content frame
        content_frame = tk.Frame(parent)
        content_frame.pack(side="right", fill="both", expand=True)
        
        # Content title
        self.content_title = tk.Label(content_frame, text="", font=("Arial", 22, "bold"))
        self.content_title.pack(anchor="w", pady=(0, 10))
        
        # Text area with scrollbar
        text_container = tk.Frame(content_frame)
        text_container.pack(fill="both", expand=True)
        
        # Text widget
        self.text_widget = tk.Text(
            text_container,
            wrap="word",
            font=("Arial", 12),
            padx=15,
            pady=15,
            state="disabled"
        )
        self.text_widget.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        text_scrollbar = tk.Scrollbar(text_container, command=self.text_widget.yview)
        text_scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=text_scrollbar.set)

    def load_help_content(self):
        """Load and parse the help content from help_menu.txt"""
        help_path = "ui_modules/help_menu.txt"
        
        if not os.path.exists(help_path):
            self.show_fallback_content()
            return
        
        try:
            with open(help_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse sections
            self.parse_sections(content)
            self.create_section_buttons()
            self.show_section(0)  # Show first section by default
            
        except Exception as e:
            self.show_fallback_content()

    def parse_sections(self, content):
        """Parse the help content into sections"""
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if line is a section header (starts with ** and ends with **)
            if line.strip().startswith('**') and line.strip().endswith('**'):
                # Save previous section if exists
                if current_section:
                    self.sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip()
                    })
                
                # Start new section
                current_section = line.strip()[2:-2]  # Remove ** markers
                current_content = []
            else:
                if current_section is not None:
                    current_content.append(line)
        
        # Add the last section
        if current_section:
            self.sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip()
            })

    def create_section_buttons(self):
        """Create clickable buttons for each section in the sidebar"""
        for i, section in enumerate(self.sections):
            btn = tk.Button(
                self.sections_frame,
                text=section['title'],
                font=("Arial", 12),
                anchor="w",
                relief="flat",
                bd=0,
                padx=10,
                pady=5,
                command=lambda idx=i: self.show_section(idx)
            )
            btn.pack(fill="x", pady=1)
            
            # Bind hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#e0e0e0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="SystemButtonFace"))

    def show_section(self, section_index):
        """Display the selected section content"""
        if 0 <= section_index < len(self.sections):
            self.current_section = section_index
            section = self.sections[section_index]
            
            # Update title
            self.content_title.config(text=section['title'])
            
            # Update content
            self.text_widget.config(state="normal")
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", section['content'])
            self.text_widget.config(state="disabled")
            
            # Scroll to top
            self.text_widget.yview_moveto(0)

    def show_fallback_content(self):
        """Show fallback content if help file is not found"""
        fallback_content = (
            "HELP\n\n"
            "Train: Enter to submit; Shift+Enter newline.\n"
            "Summarize: Requires API key; Save as .txt.\n"
            "Chat: Requires API key; Save/View/Export chats.\n"
            "Colors: Name/hex; XKCD browser; Saved for Later.\n"
            "Associations: Search, edit, delete; export to Excel.\n"
            "Tip: Add a full help_menu.txt to replace this fallback."
        )
        
        self.sections = [{
            'title': 'Help',
            'content': fallback_content
        }]
        
        self.create_section_buttons()
        self.show_section(0) 