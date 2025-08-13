import tkinter as tk
from tkinter import messagebox
import os
import webbrowser


class APIKeyPopup:
    def __init__(self, parent, refresh_callback=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.api_key_var = tk.StringVar()
        self.create_popup()

    def create_popup(self):
        """Create the API key popup window"""
        # Create popup window
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Add an API Key")
        self.popup.geometry("450x300")
        
        # Center the popup
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.popup.winfo_screenheight() // 2) - (300 // 2)
        self.popup.geometry(f"450x300+{x}+{y}")
        
        # Make it modal
        self.popup.transient(self.parent)
        self.popup.grab_set()
        
        # Prevent resizing
        self.popup.resizable(False, False)
        
        # Create main container
        main_frame = tk.Frame(self.popup, padx=30, pady=30)
        main_frame.pack(expand=True, fill="both")
        
        # Title
        title_label = tk.Label(main_frame, text="Follow these simple steps to get your API key:", 
                              font=("Arial", 14, "bold"))
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Step 1
        step1_frame = tk.Frame(main_frame)
        step1_frame.pack(anchor="w", pady=(0, 15))
        
        step1_text = tk.Label(step1_frame, text="1. Go to", font=("Arial", 12))
        step1_text.pack(side="left")
        
        # Website link
        link_label = tk.Label(step1_frame, text="this website.", 
                             font=("Arial", 12), fg="blue", cursor="hand2")
        link_label.pack(side="left")
        link_label.bind("<Button-1>", self.open_website)
        link_label.bind("<Enter>", lambda e: link_label.config(fg="darkblue"))
        link_label.bind("<Leave>", lambda e: link_label.config(fg="blue"))
        
        # Step 2
        step2_label = tk.Label(main_frame, text="2. Click \"Create API Key,\" select Gemini API, and generate a new key.", 
                              font=("Arial", 12), wraplength=440, justify="left")
        step2_label.pack(anchor="w", pady=(0, 15))
        
        # Step 3
        step3_label = tk.Label(main_frame, text="3. Copy your new API key and paste it below.", 
                              font=("Arial", 12))
        step3_label.pack(anchor="w", pady=(0, 10))
        
        # API key label
        api_key_label = tk.Label(main_frame, text="Your API key:", font=("Arial", 12))
        api_key_label.pack(anchor="w", pady=(0, 5))
        
        # API key entry
        self.api_key_entry = tk.Entry(main_frame, textvariable=self.api_key_var, 
                                     font=("Arial", 12), width=50, show="*")
        self.api_key_entry.pack(anchor="w", pady=(0, 20))
        
        # Save button
        save_button = tk.Button(main_frame, text="Save", command=self.save_api_key,
                               font=("Arial", 12), width=10)
        save_button.pack(anchor="w")
        
        # Focus on the entry field
        self.api_key_entry.focus()
        
        # Bind Enter key to save
        self.popup.bind("<Return>", lambda e: self.save_api_key())

    def open_website(self, event=None):
        """Open the Google AI Studio website"""
        webbrowser.open("https://aistudio.google.com/app/apikey")

    def save_api_key(self):
        """Save the API key to .env file"""
        api_key = self.api_key_var.get().strip()
        
        if not api_key:
            messagebox.showwarning("Invalid API Key", "Please enter an API key.")
            return
        
        try:
            # Create .env file content
            env_content = f"GOOGLE_GENERATIVE_AI_API_KEY=\"{api_key}\"\n"
            
            # Write to .env file
            with open(".env", "w") as f:
                f.write(env_content)
            
            messagebox.showinfo("Success", "API key saved successfully!")
            self.popup.destroy()
            
            # Call refresh callback if provided
            if self.refresh_callback:
                self.refresh_callback()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {str(e)}") 
