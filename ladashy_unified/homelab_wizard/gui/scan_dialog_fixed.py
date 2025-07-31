"""
Network scanning progress dialog with working progress bar
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class ScanProgressDialog:
    def __init__(self, parent, scanner):
        self.scanner = scanner
        self.parent = parent
        self.discovered = {}
        self.cancelled = False
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Scanning Network")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel_scan)
        
        self.setup_ui()
        
        # Start scanning
        self.start_scan()
        
    def setup_ui(self):
        """Setup the progress dialog"""
        # Progress label
        self.progress_var = tk.StringVar(value="Initializing scan...")
        progress_label = ttk.Label(self.dialog, textvariable=self.progress_var)
        progress_label.pack(pady=10)
        
        # Progress bar - use determinate mode with manual updates
        self.progress_value = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.dialog, 
            variable=self.progress_value,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill='x', padx=20, pady=5)
        
        # Output text
        text_frame = ttk.Frame(self.dialog)
        text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(text_frame, height=15, width=70)
        self.output_text.pack(fill='both', expand=True)
        
        # Configure text tags for colored output
        self.output_text.tag_config('info', foreground='blue')
        self.output_text.tag_config('success', foreground='green')
        self.output_text.tag_config('warning', foreground='orange')
        self.output_text.tag_config('error', foreground='red')
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', pady=10)
        
        self.close_btn = ttk.Button(button_frame, text="Cancel", 
                                   command=self.cancel_scan)
        self.close_btn.pack(side='right', padx=20)
        
    def start_scan(self):
        """Start the network scan"""
        self.scan_thread = threading.Thread(target=self.scan_worker, daemon=True)
        self.scan_thread.start()
        
    def scan_worker(self):
        """Worker thread for scanning"""
        try:
            # Track progress
            self.total_steps = 0
            self.current_step = 0
            
            # Count total hosts to scan
            networks = self.scanner.get_networks()
            estimated_hosts = len(networks) * 254  # Rough estimate
            
            # Custom progress callback
            def progress_with_bar(message):
                if not self.cancelled:
                    self.current_step += 1
                    progress = min((self.current_step / max(estimated_hosts, 1)) * 100, 99)
                    self.update_progress(message, progress)
            
            # Scan for services
            self.discovered = self.scanner.discover_all_services(
                progress_callback=progress_with_bar
            )
            
            # Update UI when done
            if not self.cancelled:
                self.dialog.after(0, self.scan_complete)
            
        except Exception as e:
            if not self.cancelled:
                self.dialog.after(0, self.scan_error, str(e))
    
    def update_progress(self, message, progress_percent=None):
        """Update progress in UI"""
        if not self.cancelled:
            self.dialog.after(0, self._update_progress_ui, message, progress_percent)
        
    def _update_progress_ui(self, message, progress_percent):
        """Update UI from main thread"""
        self.progress_var.set(message)
        
        # Update progress bar if percentage provided
        if progress_percent is not None:
            self.progress_value.set(progress_percent)
        
        # Color code messages
        if "error:" in message.lower():
            self.output_text.insert(tk.END, f"{message}\n", 'error')
        elif "warning:" in message.lower():
            self.output_text.insert(tk.END, f"{message}\n", 'warning')
        elif "found:" in message.lower():
            self.output_text.insert(tk.END, f"✓ {message}\n", 'success')
        elif "scanning" in message.lower():
            self.output_text.insert(tk.END, f"→ {message}\n", 'info')
        else:
            self.output_text.insert(tk.END, f"{message}\n")
            
        self.output_text.see(tk.END)
        self.output_text.update()
        
    def scan_complete(self):
        """Handle scan completion"""
        self.progress_value.set(100)
        self.progress_var.set("Scan complete!")
        self.close_btn.config(text="Close")
        
        # Show summary
        total_hosts = len(self.discovered)
        total_services = sum(len(h['services']) for h in self.discovered.values())
        
        summary = f"\n{'='*50}\n"
        summary += f"Scan Complete!\n"
        summary += f"Found {total_hosts} hosts with {total_services} services\n"
        summary += f"{'='*50}\n"
        
        self.output_text.insert(tk.END, summary, 'success')
        self.output_text.see(tk.END)
        
    def scan_error(self, error):
        """Handle scan error"""
        self.progress_var.set("Scan error!")
        self.output_text.insert(tk.END, f"\nERROR: {error}\n", 'error')
        self.close_btn.config(text="Close")
        
    def cancel_scan(self):
        """Cancel or close the scan"""
        self.cancelled = True
        self.dialog.destroy()
    
    def get_results(self):
        """Get scan results"""
        return self.discovered
