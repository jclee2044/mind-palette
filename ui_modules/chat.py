import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from gemini_backend import generate_chat_response, has_api_key
from key_bindings import apply_text_navigation_bindings, bind_enter_to_submit
from utils import load_database, setup_cross_platform_scrolling, get_link_colors
from ui_modules.popups.api_key_popup import APIKeyPopup


class ChatTab:
    def __init__(self, parent, refresh_all_callback=None):
        self.parent = parent
        self.refresh_all_callback = refresh_all_callback
        self.setup_ui()

    def setup_ui(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Check if API key is available
        if not has_api_key():
            self.show_api_key_message()
            return

        tk.Label(self.parent, text="Enter your prompt:").pack(pady=5)
        self.chat_entry = tk.Text(self.parent, height=4, width=60, wrap="word")
        self.chat_entry.pack(pady=5)
        bind_enter_to_submit(self.chat_entry, self.generate_chat)
        apply_text_navigation_bindings(self.chat_entry)

        self.chat_button = tk.Button(self.parent, text="Generate Response", command=self.generate_chat)
        self.chat_button.pack(pady=5)

        self.chat_output_frame = tk.Frame(self.parent)
        self.chat_output_frame.pack(padx=80, pady=10, fill="both", expand=True)

        self.chat_response_text = tk.Text(self.chat_output_frame, wrap="word", height=10)
        self.chat_response_text.config(state="disabled")
        self.chat_response_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.chat_output_frame, command=self.chat_response_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_response_text.config(yscrollcommand=scrollbar.set)
        
        # Set up cross-platform scrolling
        setup_cross_platform_scrolling(self.chat_response_text)

        # Button frame with Save, View, Export
        chat_button_frame = tk.Frame(self.parent)
        chat_button_frame.pack(pady=5)

        # Save Chat button
        self.save_chat_button = tk.Button(chat_button_frame, text="Save Chat", command=self.save_chat_to_file)
        self.save_chat_button.pack(side="left", padx=(0, 5))

        # View Saved Chats button
        self.view_chats_button = tk.Button(chat_button_frame, text="View Saved Chats", command=self.view_saved_chats)
        self.view_chats_button.pack(side="left", padx=(0, 5))

        # Export to TXT button
        self.export_chat_button = tk.Button(chat_button_frame, text="Export to .txt", command=self.export_chat_response)
        self.export_chat_button.pack(side="left", padx=(5, 0))

    def generate_chat(self):
        prompt = self.chat_entry.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showinfo("Chat", "Please enter a prompt.")
            return

        db = load_database()
        if not db:
            messagebox.showinfo("Chat", "Database is empty.")
            return

        try:
            response = generate_chat_response(prompt, db)
            self.chat_response_text.config(state="normal")
            self.chat_response_text.delete("1.0", tk.END)
            self.chat_response_text.insert("1.0", response)
            self.chat_response_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate response: {str(e)}")

    def save_chat_to_file(self):
        prompt = self.chat_entry.get("1.0", tk.END).strip()
        self.chat_response_text.config(state="normal")
        response = self.chat_response_text.get("1.0", tk.END).strip()
        self.chat_response_text.config(state="disabled")

        if not prompt or not response:
            messagebox.showinfo("Save Chat", "Prompt and response must both be present.")
            return

        save_path = "db/saved_chats.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Load existing chats if available
        if os.path.exists(save_path):
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    saved_chats = json.load(f)
            except json.JSONDecodeError:
                saved_chats = []
        else:
            saved_chats = []

        # Append the new prompt/response
        saved_chats.append({
            "prompt": prompt,
            "response": response
        })

        # Save the updated list
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(saved_chats, f, indent=4)

        messagebox.showinfo("Saved", "Chat saved to db/saved_chats.json")

    def view_saved_chats(self):
        save_path = "db/saved_chats.json"
        if not os.path.exists(save_path):
            messagebox.showinfo("View Chats", "No saved chats found.")
            return

        try:
            with open(save_path, "r", encoding="utf-8") as f:
                saved_chats = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Failed to load saved chats.")
            return

        if not saved_chats:
            messagebox.showinfo("View Chats", "No saved chats available.")
            return

        # Create popup window
        window = tk.Toplevel(self.parent)
        window.title("Saved Chats")
        window.geometry("850x550")

        # Center the popup window
        window.update_idletasks()
        w = 850
        h = 550
        x = (window.winfo_screenwidth() // 2) - (w // 2)
        y = (window.winfo_screenheight() // 2) - (h // 2)
        window.geometry(f"{w}x{h}+{x}+{y}")

        window.transient(self.parent)
        window.grab_set()

        # Layout: Listbox (left) + Prompt/Response (right)
        list_frame = tk.Frame(window)
        list_frame.pack(side="left", fill="y", padx=(10, 0), pady=10)

        detail_frame = tk.Frame(window)
        detail_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Listbox for prompts
        listbox = tk.Listbox(list_frame, width=40, font=("Arial", 14))
        listbox.pack(fill="y", expand=True)

        list_scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        list_scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=list_scrollbar.set)

        # Right panel: Prompt label and textbox
        tk.Label(detail_frame, text="Prompt:", font=("Arial", 14, "bold")).pack(anchor="w")
        prompt_text = tk.Text(detail_frame, height=3, wrap="word", font=("Arial", 14))
        prompt_text.pack(fill="x", pady=(0, 10))
        prompt_text.config(state="disabled")

        # Right panel: Response label and textbox
        tk.Label(detail_frame, text="Response:", font=("Arial", 14, "bold")).pack(anchor="w")
        response_text = tk.Text(detail_frame, height=12, wrap="word", font=("Arial", 14))
        response_text.pack(fill="both", expand=True)
        response_text.config(state="disabled")

        # Populate listbox with prompt previews
        for i, chat in enumerate(saved_chats):
            preview = chat["prompt"].strip().replace("\n", " ")
            if len(preview) > 80:
                preview = preview[:77] + "..."
            listbox.insert(tk.END, preview)

        # Display full chat when selected
        def on_select(event):
            selection = listbox.curselection()
            if not selection:
                return
            index = selection[0]
            chat = saved_chats[index]

            prompt_text.config(state="normal")
            prompt_text.delete("1.0", tk.END)
            prompt_text.insert(tk.END, chat["prompt"].strip())
            prompt_text.config(state="disabled")

            response_text.config(state="normal")
            response_text.delete("1.0", tk.END)
            response_text.insert(tk.END, chat["response"].strip())
            response_text.config(state="disabled")

        listbox.bind("<<ListboxSelect>>", on_select)

        # Delete selected chat with Delete or Backspace
        def delete_selected_chat(event=None):
            selection = listbox.curselection()
            if not selection:
                return
            index = selection[0]

            confirm = messagebox.askyesno("Delete Chat", "Delete this saved chat?")
            if not confirm:
                return

            del saved_chats[index]
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(saved_chats, f, indent=4)

            listbox.delete(index)

            prompt_text.config(state="normal")
            prompt_text.delete("1.0", tk.END)
            prompt_text.config(state="disabled")

            response_text.config(state="normal")
            response_text.delete("1.0", tk.END)
            response_text.config(state="disabled")

        listbox.bind("<Delete>", delete_selected_chat)
        listbox.bind("<BackSpace>", delete_selected_chat)

    def export_chat_response(self):
        # Temporarily enable the text widget to get its content
        self.chat_response_text.config(state="normal")
        response_text = self.chat_response_text.get("1.0", tk.END).strip()
        self.chat_response_text.config(state="disabled")
        
        if not response_text:
            messagebox.showinfo("Export", "No response to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Chat Response"
        )

        if not file_path:
            return  # User canceled

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response_text)
            messagebox.showinfo("Export", f"Response exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export response: {str(e)}") 

    def show_api_key_message(self):
        """Display message when API key is missing"""
        # Create a centered container
        container = tk.Frame(self.parent)
        container.pack(expand=True, fill="both")
        
        # Center the content vertically and horizontally
        center_frame = tk.Frame(container)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Main message
        message_label = tk.Label(center_frame, text="You need an API key to use this.", 
                                font=("Arial", 14))
        message_label.pack(pady=(0, 10))
        
        # Get appropriate link colors for current system appearance
        normal_color, hover_color, _ = get_link_colors()
        
        # Link to add API key
        link_label = tk.Label(center_frame, text="Add one (it's easy!)", 
                             font=("Arial", 13), fg=normal_color, cursor="hand2")
        link_label.pack()
        
        # Bind click event to the link
        link_label.bind("<Button-1>", self.open_api_key_help)
        link_label.bind("<Enter>", lambda e: link_label.config(fg=hover_color))
        link_label.bind("<Leave>", lambda e: link_label.config(fg=normal_color))

    def open_api_key_help(self, event=None):
        """Open help for adding API key"""
        callback = self.refresh_all_callback if self.refresh_all_callback else self.setup_ui
        APIKeyPopup(self.parent, refresh_callback=callback) 