import os
import sys
import ast

project_dir = r"C:\bot\2601\gachabot"
sys.path.insert(0, project_dir)

errors = []

for root, _, files in os.walk(project_dir):
    if "venv" in root or ".git" in root or "join_sim" in root:
        continue
    
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            try:
                tree = ast.parse(content, filename=full_path)
            except SyntaxError as e:
                errors.append((full_path, f"SyntaxError: {e}"))
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            __import__(alias.name)
                        except ImportError as e:
                            errors.append((full_path, f"ImportError: {e} (import {alias.name})"))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            # Try to import the module
                            __import__(node.module)
                        except ImportError as e:
                            errors.append((full_path, f"ImportError: {e} (from {node.module} import ...)"))

if errors:
    for path, err in errors:
        print(f"ERROR IN: {path}")
        print(err)
        print("-" * 50)
else:
    print("NO IMPORT ERRORS FOUND")
