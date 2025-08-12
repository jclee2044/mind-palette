def apply_text_navigation_bindings(widget):
    """
    Adds Ctrl+A to select all, Home to move to line start, and End to move to line end.
    """
    widget.bind("<Control-a>", lambda e: (widget.tag_add("sel", "1.0", "end"), "break"))
    widget.bind("<Home>", lambda e: (widget.mark_set("insert", "insert linestart"), "break"))
    widget.bind("<End>", lambda e: (widget.mark_set("insert", "insert lineend"), "break"))

def bind_enter_to_submit(widget, submit_callback):
    """
    Binds Enter to trigger the submit_callback and Shift+Enter to insert a newline.
    """
    def on_enter(event):
        if event.state & 0x0001:  # Shift key held down
            return  # Allow newline
        submit_callback()
        return "break"  # Prevent newline insertion

    widget.bind("<Return>", on_enter)
    widget.bind("<Shift-Return>", lambda e: None)
