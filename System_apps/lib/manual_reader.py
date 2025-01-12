import json
import os
import time
import textwrap
import lib.graphic as gr
import lib.input as input

class ManualReader:
    def __init__(self, manuals_root):
        self.manuals_root = manuals_root
        self.selected_position = 0
        self.scroll_offset = 0
        self.content_scroll = 0
        self.visible_items = 7
        self.path_history = []
        self.current_items = []
        self.menu_len = 0
        self.in_manual = False
        self.in_section = False
        self.current_manual_data = None
        self.current_section = None
        self._load_current_directory()
    
    def _load_current_directory(self):
        """Carga el contenido del directorio actual"""
        current_path = os.path.join(self.manuals_root, *self.path_history)
        self.current_items = []
        
        try:
            items = os.listdir(current_path)
            
            # Primero directorios
            for item in sorted(items):
                full_path = os.path.join(current_path, item)
                if os.path.isdir(full_path):
                    self.current_items.append({"name": item, "type": "dir"})
            
            # Luego archivos JSON
            for item in sorted(items):
                if item.endswith('.json'):
                    self.current_items.append({
                        "name": item[:-5],
                        "type": "file"
                    })
                    
            self.menu_len = len(self.current_items)
            
        except Exception as e:
            print(f"Error loading directory: {e}")
            self.current_items = []
            self.menu_len = 0

    def _load_json(self, json_path):
        """Carga un archivo JSON"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading manual: {e}")
            return {}

    def get_current_path(self):
        if not self.path_history:
            return "/"
        return "/" + "/".join(self.path_history)

    def move_cursor(self):
        if input.value == 1:  # Moving down
            if not self.in_section:
                # Navegación normal en menús
                if self.selected_position < (self.menu_len - 1):
                    self.selected_position += 1
                    if self.selected_position - self.scroll_offset >= self.visible_items:
                        self.scroll_offset += 1
            else:
                # Scroll del contenido
                self.content_scroll = min(self.content_scroll + 20, self.get_max_scroll())
        elif input.value == -1:  # Moving up
            if not self.in_section:
                # Navegación normal en menús
                if self.selected_position > 0:
                    self.selected_position -= 1
                    if self.selected_position < self.scroll_offset:
                        self.scroll_offset -= 1
            else:
                # Scroll del contenido
                self.content_scroll = max(0, self.content_scroll - 20)

    def get_max_scroll(self):
        """Calcula el máximo scroll posible para el contenido actual"""
        if not self.in_section or not self.current_section:
            return 0
            
        # Con draw_log el scroll es manejado internamente
        return 0

    def draw_menu(self):
        gr.draw_clear()
        
        # Contenedor principal
        gr.draw_rectangle_r([10, 40, 630, 440], 15, fill=gr.colorGrayD2, outline=None)
        gr.draw_text((320, 20), "Manual Reader", anchor="mm")
        
        # Ruta actual
        current_path = self.get_current_path()
        gr.draw_text((320, 60), current_path, anchor="mm")

        if self.in_manual:
            if self.in_section:
                self._draw_section_content()
            else:
                self._draw_manual_sections()
        else:
            self._draw_directory_content()

        # Botones
        button_circle((133, 440), "B", "Back")
        button_circle((320, 440), "A", "Select")

        gr.draw_paint()

    def _draw_directory_content(self):
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_items, len(self.current_items))

        if self.scroll_offset > 0:
            gr.draw_text((320, 120), "▲", anchor="mm")
        if end_idx < len(self.current_items):
            gr.draw_text((320, 410), "▼", anchor="mm")

        for i in range(start_idx, end_idx):
            relative_pos = i - start_idx
            y_pos = 130 + (relative_pos * 40)
            item = self.current_items[i]
            icon = "📁 " if item["type"] == "dir" else "📄 "
            text = icon + item["name"]
            row_list(text, (20, y_pos), 600, i == self.selected_position)

    def _draw_manual_sections(self):
        sections = list(self.current_manual_data.keys())
        self.menu_len = len(sections)
        
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.visible_items, len(sections))

        if self.scroll_offset > 0:
            gr.draw_text((320, 120), "▲", anchor="mm")
        if end_idx < len(sections):
            gr.draw_text((320, 410), "▼", anchor="mm")

        for i in range(start_idx, end_idx):
            relative_pos = i - start_idx
            y_pos = 130 + (relative_pos * 40)
            text = sections[i]
            row_list(text, (20, y_pos), 600, i == self.selected_position)

    def _draw_section_content(self):
        if not self.current_section or not self.current_manual_data:
            return

        try:
            content = self.current_manual_data[self.current_section]
            
            # Preparar el contenido con espaciado optimizado
            display_text = f"{self.current_section}\n\n"
            for step, description in content.items():
                description = description.replace('\n', ' ').strip()
                wrapped_step = textwrap.wrap(step, width=50)
                wrapped_desc = textwrap.wrap(description, width=50)
                display_text += "\n".join(wrapped_step) + "\n" + "\n".join(wrapped_desc) + "\n\n"

            gr.draw_log(
                display_text,
                fill=gr.colorBlue,
                outline=gr.colorBlueD1,
                width=600,
                height=340,
                centered=False
            )

        except Exception as e:
            print(f"Error drawing section content: {e}")
            gr.draw_log(f"Error: {str(e)}", fill=gr.colorBlue, outline=gr.colorBlueD1)

    def handle_input(self):
        if input.key("DY"):
            self.move_cursor()
                
        elif input.key("A"):
            if not self.in_manual and self.current_items:
                selected_item = self.current_items[self.selected_position]
                
                if selected_item["type"] == "dir":
                    self.path_history.append(selected_item["name"])
                    self.selected_position = 0
                    self.scroll_offset = 0
                    self._load_current_directory()
                else:
                    json_path = os.path.join(
                        self.manuals_root, 
                        *self.path_history, 
                        f"{selected_item['name']}.json"
                    )
                    self.current_manual_data = self._load_json(json_path)
                    self.in_manual = True
                    self.in_section = False
                    self.current_section = None
                    self.selected_position = 0
                    self.scroll_offset = 0
                    
            elif self.in_manual and not self.in_section:
                sections = list(self.current_manual_data.keys())
                if 0 <= self.selected_position < len(sections):
                    self.current_section = sections[self.selected_position]
                    self.in_section = True
                    self.content_scroll = 0
                
        elif input.key("B"):
            if self.in_section:
                self.in_section = False
                self.current_section = None
                self.content_scroll = 0
            elif self.in_manual:
                self.in_manual = False
                self.current_manual_data = None
                self.selected_position = 0
                self.scroll_offset = 0
            elif self.path_history:
                self.path_history.pop()
                self.selected_position = 0
                self.scroll_offset = 0
                self._load_current_directory()
            else:
                return False
                
        return True

    def update(self):
        continue_running = True
        
        input.check()
        
        if input.key("MENUF"):
            return False

        continue_running = self.handle_input()
        self.draw_menu()
        
        return continue_running

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