#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import our app module
try:
    import app
except Exception as e:
    print(f"Error importing app module: {e}")
    sys.exit(1)

def main():
    try:
        app.start()
        while True:
            app.update()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error in main(): {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()