#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import graphic as gr
import input

current_window = "main"
selected_position = 0
scroll_offset = 0  # Track scroll position
visible_items = 7  # Number of items visible at once
menu_len = 10
app_name = "SystemApps"

def get_options():
    ssh_status = check_service_status("ssh")
    scp_status = check_service_status("scp")
    battery_percentage = get_battery_percentage()
    options = []
    
    options.append(("Disable SSH" if ssh_status else "Enable SSH", "ssh"))
    options.append(("Disable SCP" if scp_status else "Enable SCP", "scp"))
    options.append(("Show Battery Level", "battery"))
    options.append(("Show Battery Details", "battery_info"))
    options.append(("Show Local IP", "ip"))
    options.append(("Sync System Time", "sync"))
    options.append(("Show RAM Status", "ram"))
    options.append(("Clean RAM", "clean_ram"))
    options.append(("Clean Packages", "clean_pkg"))
    options.append(("Exit", "exit"))

    return options, ssh_status, scp_status

def get_battery_percentage():
    try:
        with open('/sys/class/power_supply/axp2202-battery/capacity', 'r') as f:
            return f"{f.read().strip()}%"
    except:
        return "N/A"

def get_battery_info():
    try:
        info = {}
        files = ['status', 'capacity', 'voltage_now', 'current_now', 'health']
        
        for file in files:
            try:
                with open(f'/sys/class/power_supply/axp2202-battery/{file}', 'r') as f:
                    info[file] = f.read().strip()
            except:
                info[file] = 'N/A'
        
        voltage = 'N/A' if info['voltage_now'] == 'N/A' else f"{int(info['voltage_now'])/1000000:.2f}V"
        current = 'N/A' if info['current_now'] == 'N/A' else f"{int(info['current_now'])/1000000:.2f}A"
        
        return (f"Status: {info['status']}\n"
                f"Battery Level: {info['capacity']}%\n"
                f"Voltage: {voltage}\n"
                f"Current: {current}\n"
                f"Health: {info['health']}")
    except Exception as e:
        return f"Battery information not available"

def get_local_ip():
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        return result.stdout.strip().split()[0]
    except:
        return "IP not available"

def get_ram_info():
    """Get RAM usage information"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GetRAM.sh")
        subprocess.run(['bash', script_path], check=True)
        
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.txt"), 'r') as f:
            ram_info = json.loads(f.read().strip())
        return ram_info
    except Exception as e:
        print(f"Error getting RAM info: {e}")
        return {"total": 0, "used": 0, "available": 0, "usage_percent": 0}
    
def show_ram_status():
    """Shows RAM status in a message box"""
    ram_info = get_ram_info()
    ram_text = f"RAM Usage: {ram_info['usage_percent']}%\nUsed: {ram_info['used']}MB / {ram_info['total']}MB\nAvailable: {ram_info['available']}MB"
    gr.draw_clear()
    gr.draw_log(ram_text, fill=gr.colorBlue, outline=gr.colorBlueD1, height=120, centered=False)
    gr.draw_paint()
    time.sleep(3)
    return

def check_scp_config():
    """Verifica si la configuración actual tiene SCP habilitado"""
    try:
        with open('/etc/ssh/sshd_config', 'r') as f:
            config = f.read()
            return 'AllowTcpForwarding yes' in config
    except:
        return False

def check_service_status(service_type):
    """Verifica el estado de los servicios"""
    if service_type == "ssh":
        try:
            result = subprocess.run(['systemctl', 'is-active', 'ssh'], 
                                capture_output=True, text=True)
            return result.stdout.strip() == 'active'
        except:
            return False
    else:  # scp
        return check_service_status("ssh") and check_scp_config()

def row_list(text, pos, width, selected):
    gr.draw_rectangle_r(
        [pos[0], pos[1], pos[0] + width, pos[1] + 32],
        5,
        fill=(gr.colorBlue if selected else gr.colorGrayL1),
    )
    gr.draw_text((pos[0] + 5, pos[1] + 5), text)

def button_circle(pos, button, text):
    gr.draw_circle(pos, 25, fill=gr.colorBlueD1)
    gr.draw_text((pos[0] + 12, pos[1] + 12), button, anchor="mm")
    gr.draw_text((pos[0] + 30, pos[1] + 12), text, font=13, anchor="lm")


def show_message(msg='Processing...', colorFill=gr.colorBlue):
    """Muestra el mensaje de procesamiento"""
    gr.draw_clear()
    gr.draw_log(msg, fill=colorFill, outline=gr.colorBlueD1)
    gr.draw_paint()

def execute_script(script_path):
    try:
        show_message('Processing...')
        subprocess.run(['bash', script_path], check=True)
        show_message('Success!', gr.colorGreen)
        time.sleep(1)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")
        return False

def start():
    print(f"Starting {app_name}...")
    load_main_menu()

def update():
    global current_window, selected_position

    input.check()

    if input.key("MENUF"):
        gr.draw_end()
        print(f"Starting {app_name}...")
        sys.exit()

    load_main_menu()

def move_cursor_dy(auto_move: bool = False):
    global selected_position, scroll_offset
    
    if auto_move or input.value == 1:  # Moving down
        if selected_position < menu_len - 1:
            selected_position += 1
            # If selection moves beyond visible area, scroll down
            if selected_position - scroll_offset >= visible_items:
                scroll_offset += 1
    elif input.value == -1:  # Moving up
        if selected_position > 0:
            selected_position -= 1
            # If selection moves above visible area, scroll up
            if selected_position < scroll_offset:
                scroll_offset -= 1

def auto_move_cursor():
    move_cursor_dy(True)

def load_main_menu():
    options, ssh_status, scp_status = get_options()
    
    if input.key("DY"):
        move_cursor_dy(False)
    elif input.key("A"):
        service_type = options[selected_position][1]
        toggle_service(service_type)

    gr.draw_clear()

    # Draw main container
    gr.draw_rectangle_r([10, 40, 630, 440], 15, fill=gr.colorGrayD2, outline=None)
    gr.draw_text((320, 20), app_name, anchor="mm")

    # Draw status
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gr.draw_text((320, 60), "SSH Status: " + ("Active" if ssh_status else "Inactive"), anchor="mm")
    gr.draw_text((320, 80), "SCP Status: " + ("Active" if scp_status else "Inactive"), anchor="mm")
    gr.draw_text((320, 100), f"Current Time: {current_time}", anchor="mm")

    # Calculate visible range
    start_idx = scroll_offset
    end_idx = min(start_idx + visible_items, len(options))

    # Draw scroll indicators if needed
    if scroll_offset > 0:
        gr.draw_text((320, 120), "▲", anchor="mm")  # Up arrow
    if end_idx < len(options):
        gr.draw_text((320, 410), "▼", anchor="mm")  # Down arrow

    # Draw visible options
    for i in range(start_idx, end_idx):
        relative_pos = i - start_idx  # Position relative to visible window
        y_pos = 130 + (relative_pos * 40)  # 40 pixels between items
        text, _ = options[i]
        row_list(text, (20, y_pos), 600, i == selected_position)

    # Draw buttons
    button_circle((133, 440), "F", "Exit")
    button_circle((320, 440), "A", "Select")

    gr.draw_paint()

def toggle_service(service_type):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script = None

    if service_type == "ssh":
        script = os.path.join(current_dir, "EnableSSH.sh" if not check_service_status("ssh") else "DisableSSH.sh")
    elif service_type == "scp":
        if check_service_status("ssh"):
            script = os.path.join(current_dir, "EnableSCP.sh" if not check_scp_config() else "DisableSCP.sh")
        else:
            script = os.path.join(current_dir, "EnableSCP.sh")
    elif service_type == "battery":
        percentage = get_battery_percentage()
        gr.draw_clear()
        gr.draw_log(f"Battery Level: {percentage}", fill=gr.colorBlue, outline=gr.colorBlueD1)
        gr.draw_paint()
        time.sleep(3)
        return
    elif service_type == "battery_info":
        battery_info = get_battery_info()
        gr.draw_clear()
        gr.draw_log(battery_info, fill=gr.colorBlue, outline=gr.colorBlueD1, height=150, centered=False)
        gr.draw_paint()
        time.sleep(5)
        return
    elif service_type == "ip":
        local_ip = get_local_ip()
        gr.draw_clear()
        gr.draw_log(f"Local IP: {local_ip}", fill=gr.colorBlue, outline=gr.colorBlueD1)
        gr.draw_paint()
        time.sleep(3)
        return
    elif service_type == "sync":
        script = os.path.join(current_dir, "SyncTime.sh")
    elif service_type == "ram":
        show_ram_status()
        return
    elif service_type == "clean_ram":
        script = os.path.join(current_dir, "CleanRAM.sh")
    elif service_type == "clean_pkg":
        script = os.path.join(current_dir, "CleanPKG.sh")
    elif service_type == "exit":
        sys.exit()
            
    if script and os.path.exists(script):
        execute_script(script)
