# Add this to scan_dialog.py to show confidence

    def update_progress(self, message):
        """Update progress in UI"""
        self.dialog.after(0, self._update_progress_ui, message)
        
    def _update_progress_ui(self, message):
        """Update UI from main thread"""
        self.progress_var.set(message)
        
        # Color code based on message type
        if "identified as printer" in message:
            self.output_text.insert(tk.END, f"⚠️  {message}\n", 'warning')
        elif "Found:" in message:
            self.output_text.insert(tk.END, f"✅ {message}\n", 'success')
        elif "Identifying service" in message:
            self.output_text.insert(tk.END, f"🔍 {message}\n", 'info')
        else:
            self.output_text.insert(tk.END, f"{message}\n")
            
        self.output_text.see(tk.END)
        
        # Configure text tags
        self.output_text.tag_config('warning', foreground='orange')
        self.output_text.tag_config('success', foreground='green')
        self.output_text.tag_config('info', foreground='blue')
