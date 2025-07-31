import sys

with open('homelab_wizard/gui/service_list.py', 'r') as f:
    content = f.read()

# Fix the hover effect to check if service exists in service_vars
old_on_enter = '''def on_enter(e):
            if not self.service_vars[service_name].get():
                service_frame.config(bg='#f5f5f5')'''

new_on_enter = '''def on_enter(e):
            if service_name in self.service_vars and not self.service_vars[service_name].get():
                service_frame.config(bg='#f5f5f5')'''

content = content.replace(old_on_enter, new_on_enter)

old_on_leave = '''def on_leave(e):
            if not self.service_vars[service_name].get():
                service_frame.config(bg='white')'''

new_on_leave = '''def on_leave(e):
            if service_name in self.service_vars and not self.service_vars[service_name].get():
                service_frame.config(bg='white')'''

content = content.replace(old_on_leave, new_on_leave)

with open('homelab_wizard/gui/service_list.py', 'w') as f:
    f.write(content)

print("Fixed service_list.py")
