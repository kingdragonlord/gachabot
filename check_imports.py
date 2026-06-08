import os
import sys
import importlib.util
import traceback

project_dir = r"C:\bot\2601\gachabot"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

errors = []

for root, _, files in os.walk(project_dir):
    # skip venv or other unneeded dirs if any
    if "venv" in root or ".git" in root:
        continue
    
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            # Create a module name based on relative path
            rel_path = os.path.relpath(full_path, project_dir)
            module_name = rel_path.replace(".py", "").replace("\\", ".")
            
            try:
                # Need to use __import__ or importlib
                spec = importlib.util.spec_from_file_location(module_name, full_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    # Execute module to trigger top-level imports
                    spec.loader.exec_module(module)
            except Exception as e:
                # We specifically want to catch ImportErrors
                if isinstance(e, (ImportError, ModuleNotFoundError)):
                    errors.append((full_path, traceback.format_exc()))
                elif isinstance(e, NameError):
                    errors.append((full_path, traceback.format_exc()))
                elif isinstance(e, AttributeError):
                    errors.append((full_path, traceback.format_exc()))

if errors:
    for path, err in errors:
        print(f"ERROR IN: {path}")
        print(err)
        print("-" * 50)
else:
    print("NO IMPORT ERRORS FOUND")
