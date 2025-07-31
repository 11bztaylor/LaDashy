# Replace the create_discovered_tab method in main_window.py

def create_discovered_tab(self):
    """Create discovered services tab"""
    discovered_frame = ttk.Frame(self.notebook)
    self.notebook.add(discovered_frame, text="Discovered")
    
    # Instructions
    ttk.Label(discovered_frame, text="Services discovered on your network:",
             font=('Arial', 12)).pack(pady=10)
    
    # Discovered services tree
    tree_frame = ttk.Frame(discovered_frame)
    tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    # Create treeview with hostname column
    self.discovered_tree = ttk.Treeview(
        tree_frame, 
        columns=('Hostname', 'Service', 'Ports', 'Confidence', 'Type'), 
        show='tree headings'
    )
    
    # Configure columns
    self.discovered_tree.heading('#0', text='IP Address')
    self.discovered_tree.heading('Hostname', text='Hostname')
    self.discovered_tree.heading('Service', text='Service')
    self.discovered_tree.heading('Ports', text='Ports')
    self.discovered_tree.heading('Confidence', text='Confidence')
    self.discovered_tree.heading('Type', text='Type')
    
    # Set column widths
    self.discovered_tree.column('#0', width=150)
    self.discovered_tree.column('Hostname', width=150)
    self.discovered_tree.column('Service', width=150)
    self.discovered_tree.column('Ports', width=80)
    self.discovered_tree.column('Confidence', width=80)
    self.discovered_tree.column('Type', width=100)
    
    self.discovered_tree.pack(side='left', fill='both', expand=True)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', 
                             command=self.discovered_tree.yview)
    scrollbar.pack(side='right', fill='y')
    self.discovered_tree.configure(yscrollcommand=scrollbar.set)
    
    # Control buttons
    control_frame = ttk.Frame(discovered_frame)
    control_frame.pack(fill='x', pady=10)
    
    ttk.Button(control_frame, text="Review/Edit Services", 
              command=self.review_services).pack(side='left', padx=5)
    ttk.Button(control_frame, text="Expand All", 
              command=self.expand_all).pack(side='left', padx=5)
    ttk.Button(control_frame, text="Collapse All", 
              command=self.collapse_all).pack(side='left', padx=5)

def update_discovered_services(self):
    """Update UI with discovered services"""
    # Clear tree
    for item in self.discovered_tree.get_children():
        self.discovered_tree.delete(item)
    
    # Add discovered services
    for ip, host_info in self.discovered_services.items():
        hostname = host_info.get('hostname', 'Unknown')
        
        # Determine if it's a special device
        device_type = "Host"
        if ip.endswith('.1'):
            device_type = "Gateway"
        elif self._is_docker_host(hostname):
            device_type = "Docker"
        
        # Add host as a row (not parent)
        host_item = self.discovered_tree.insert(
            '', 'end', 
            text=ip,
            values=(hostname, '', '', '', device_type),
            tags=('host',)
        )
        
        # Add services as children
        for service in host_info.get('services', []):
            ports = ', '.join(map(str, service['ports']))
            confidence = f"{service.get('confidence', 1.0) * 100:.0f}%"
            
            # Determine confidence tag
            conf_value = service.get('confidence', 1.0)
            if conf_value >= 0.9:
                conf_tag = 'high_conf'
            elif conf_value >= 0.7:
                conf_tag = 'med_conf'
            else:
                conf_tag = 'low_conf'
            
            self.discovered_tree.insert(
                host_item, 'end',
                values=(
                    '',  # No hostname for service rows
                    service['name'],
                    ports,
                    confidence,
                    service.get('device_type', '')
                ),
                tags=(conf_tag,)
            )
            
            # Auto-check the service
            if service['name'] in self.service_vars:
                self.service_vars[service['name']].set(True)
    
    # Configure tags
    self.discovered_tree.tag_configure('host', font=('Arial', 10, 'bold'))
    self.discovered_tree.tag_configure('high_conf', foreground='green')
    self.discovered_tree.tag_configure('med_conf', foreground='orange')
    self.discovered_tree.tag_configure('low_conf', foreground='red')
    
    # Auto-expand all items
    self.expand_all()
    
    # Switch to discovered tab
    self.notebook.select(2)
    
    # Update status
    total_services = sum(len(h.get('services', [])) for h in self.discovered_services.values())
    self.status_label.config(text=f"Found {total_services} services on {len(self.discovered_services)} hosts")

def expand_all(self):
    """Expand all tree items"""
    for item in self.discovered_tree.get_children():
        self.discovered_tree.item(item, open=True)

def collapse_all(self):
    """Collapse all tree items"""
    for item in self.discovered_tree.get_children():
        self.discovered_tree.item(item, open=False)

def _is_docker_host(self, hostname):
    """Check if hostname suggests Docker container"""
    docker_indicators = [
        hostname.lower() == 'unknown',
        len(hostname) == 12 and all(c in '0123456789abcdef' for c in hostname),
        'docker' in hostname.lower(),
        hostname.startswith('container'),
    ]
    return any(docker_indicators)

def review_services(self):
    """Open service review dialog"""
    from .service_override import ServiceOverrideDialog
    dialog = ServiceOverrideDialog(self.root, self.discovered_services)
    self.root.wait_window(dialog.dialog)
