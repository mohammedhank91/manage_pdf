# Tabs package initialization

import os
import sys
import importlib.util

# List of all modules in this package
__all__ = [
    'main_tab', 'convert_tab', 'compress_tab', 'merge_tab', 'split_tab'
]

# Try to ensure all modules are importable
def ensure_modules_importable():
    """Ensure all tabs modules can be imported regardless of packaging method."""
    if getattr(sys, 'frozen', False):
        # We're in a frozen/PyInstaller environment
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        package_dir = os.path.join(base_dir, 'tabs')
        
        # Add the tabs directory to sys.path if it exists
        if os.path.isdir(package_dir) and package_dir not in sys.path:
            sys.path.insert(0, package_dir)
            
        # Also check if we need to add the parent directory
        parent_dir = os.path.dirname(package_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

# Run the function to ensure modules are importable
ensure_modules_importable()

# Pre-import all modules to make sure they're available
for module_name in __all__:
    try:
        # Try to import each module
        module_path = os.path.join(os.path.dirname(__file__), f"{module_name}.py")
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Add to globals
                globals()[module_name] = module
    except Exception as e:
        print(f"Warning: Could not pre-import {module_name}: {e}")
