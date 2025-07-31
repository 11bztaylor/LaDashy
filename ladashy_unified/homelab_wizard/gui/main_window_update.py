# Add this method to main_window.py to replace update_discovered_services

def update_discovered_services(self):
    """Update UI with discovered services"""
    # Clear tree
    for item in self.discovered_tree.get_children():
        self.discovered_tree.delete(item)
    
    if not self.discovered_services:
        # No services found
        self.discovered_tree.insert('', 'end', text="No services found", values=('', '', '', '', ''))
        return
    
    # Add discovered services
    for ip, host_info in self.discovered_services.items():
        hostname = host_info.get('hostname', 'Unknown')
        services = host_info.get('services', [])
        
        # Skip if no services
        if not services:
            continue
        
        # Determine device type
        device_type = "Host"
        if ip.endswith('.1'):
            device_type = "Gateway"
        elif ip.endswith('.254'):
            device_type = "Gateway"
        elif any('docker' in s.get('device_type', '').lower() for s in services):
            device_type = "Docker Host"
        
        # Add host
        host_text = f"{ip}"
        host_item = self.discovered_tree.insert(
            '', 'end', 
            text=host_text,
            values=(hostname, '', '', '', device_type),
            tags=('host',)
        )
        
        # Add services under host
        for service in services:
            service_name = service.get('name', 'Unknown')
            ports = ', '.join(map(str, service.get('ports', [])))
            confidence = service.get('confidence', 1.0)
            confidence_text = f"{confidence * 100:.0f}%"
            
            # Skip low confidence services
            if confidence < 0.3:
                continue
            
            # Determine confidence tag
            if confidence >= 0.9:
                conf_tag = 'high_conf'
            elif confidence >= 0.7:
                conf_tag = 'med_conf'
            else:
                conf_tag = 'low_conf'
            
            self.discovered_tree.insert(
                host_item, 'end',
                values=(
                    '',  # No hostname for service rows
                    service_name,
                    ports,
                    confidence_text,
                    service.get('device_type', '')
                ),
                tags=(conf_tag,)
            )
            
            # Auto-check the service if it's in our list
            for cat_services in SERVICES.values():
                for svc in cat_services:
                    if svc['name'].lower() == service_name.lower():
                        if svc['name'] in self.service_vars:
                            self.service_vars[svc['name']].set(True)
                        break
    
    # Configure tags
    self.discovered_tree.tag_configure('host', font=('Arial', 10, 'bold'))
    self.discovered_tree.tag_configure('high_conf', foreground='green')
    self.discovered_tree.tag_configure('med_conf', foreground='orange')
    self.discovered_tree.tag_configure('low_conf', foreground='red')
    
    # Auto-expand all items
    for item in self.discovered_tree.get_children():
        self.discovered_tree.item(item, open=True)
    
    # Switch to discovered tab
    self.notebook.select(2)
    
    # Update status
    total_services = sum(len(h.get('services', [])) for h in self.discovered_services.values())
    total_hosts = len([h for h in self.discovered_services.values() if h.get('services')])
    self.status_label.config(text=f"Found {total_services} services on {total_hosts} hosts")
