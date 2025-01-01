#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import graphic as gr
import input

current_window = "main"
selected_position = 0
max_elem = 2

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
        # Para SSH solo verificamos si el servicio está activo
        try:
            result = subprocess.run(['systemctl', 'is-active', 'ssh'], 
                                capture_output=True, text=True)
            return result.stdout.strip() == 'active'
        except:
            return False
    else:  # scp
        # Para SCP verificamos si el servicio SSH está activo Y si SCP está habilitado en la configuración
        return check_service_status("ssh") and check_scp_config()

def toggle_service(service_type):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        if service_type == "ssh":
            script = os.path.join(current_dir, "EnableSSH.sh" if not check_service_status("ssh") else "DisableSSH.sh")
        else:  # scp
            if check_service_status("ssh"):
                script = os.path.join(current_dir, "EnableSCP.sh" if not check_scp_config() else "DisableSCP.sh")
            else:
                script = os.path.join(current_dir, "EnableSCP.sh")
                
        if os.path.exists(script):
            subprocess.run(['bash', script], check=True)
            time.sleep(2)
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")

def start():
    print("Starting SSH/SCP Manager...")
    load_main_menu()

def update():
    global current_window, selected_position

    input.check()

    if input.key("MENUF"):
        gr.draw_end()
        print("Exiting SSH/SCP Manager...")
        sys.exit()

    load_main_menu()

def load_main_menu():
    global selected_position

    ssh_status = check_service_status("ssh")
    scp_status = check_service_status("scp")
    options = []
    
    # Siempre mostramos ambas opciones
    options.append(("Disable SSH" if ssh_status else "Enable SSH", "ssh"))
    options.append(("Disable SCP" if scp_status else "Enable SCP", "scp"))

    if input.key("DY"):
        if input.value == 1:
            if selected_position < len(options) - 1:
                selected_position += 1
        elif input.value == -1:
            if selected_position > 0:
                selected_position -= 1
    elif input.key("A"):
        service_type = options[selected_position][1]
        toggle_service(service_type)
        gr.draw_clear()
        gr.draw_log("Procesando...", fill=gr.colorBlue, outline=gr.colorBlueD1)
        gr.draw_paint()
        time.sleep(1)

    gr.draw_clear()

    # Draw main container
    gr.draw_rectangle_r([10, 40, 630, 440], 15, fill=gr.colorGrayD2, outline=None)
    gr.draw_text((320, 20), "SSH/SCP Manager", anchor="mm")

    # Draw status
    gr.draw_text((320, 70), "SSH Status: " + ("Active" if ssh_status else "Inactive"), anchor="mm")
    gr.draw_text((320, 90), "SCP Status: " + ("Active" if scp_status else "Inactive"), anchor="mm")

    # Draw options
    for i, (text, _) in enumerate(options):
        row_list(text, (20, 150 + (i * 50)), 600, i == selected_position)

    # Draw buttons
    button_circle((133, 450), "M", "Exit")
    button_circle((320, 450), "A", "Select")

    gr.draw_paint()

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