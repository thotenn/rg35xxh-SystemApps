import sys
import os

# Get the parent directory of the current file's directory
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from lib.manual_reader import ManualReader
import lib.graphic as gr

def start_manual_reader():
    try:
        # Especificar el directorio raíz de los manuales
        manuals_root = os.path.join(current_dir, "manuals")
        
        # Crear el directorio de manuales si no existe
        os.makedirs(manuals_root, exist_ok=True)
        
        # Inicializar el lector de manuales
        reader = ManualReader(manuals_root)
        
        # Main loop
        while True:
            if not reader.update():
                break
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error in manual reader: {e}")
        
if __name__ == "__main__":
    try:
        start_manual_reader()
    finally:
        gr.draw_end()
        sys.exit()