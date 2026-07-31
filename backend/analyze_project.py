import os
import ast
from pathlib import Path

def analyze_backend(api_dir, engine_dir):
    print("--- Backend Analysis ---")
    api_files = [f for f in Path(api_dir).glob("*.py") if f.is_file() and f.name != "__init__.py"]
    
    stubs = []
    functional = []
    
    for file in api_files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # A simple heuristic: if it has "await asyncio.sleep" or heavy static "return {" without db queries/engine calls, it's likely a stub.
        if "asyncio.sleep" in content or content.count("return {") > 1 and "engine." not in content:
            stubs.append(file.name)
        else:
            functional.append(file.name)
            
    print(f"Total API Routes: {len(api_files)}")
    print(f"Likely Stubs/Mocks ({len(stubs)}): {', '.join(stubs)}")
    print(f"Functional/Wired ({len(functional)}): {', '.join(functional)}")

def analyze_engine(engine_dir):
    print("\n--- Engine Analysis ---")
    engine_folders = [f for f in Path(engine_dir).iterdir() if f.is_dir() and f.name != "__pycache__"]
    
    empty_engines = []
    implemented_engines = []
    
    for folder in engine_folders:
        py_files = list(folder.glob("*.py"))
        if not py_files or len(py_files) == 1 and py_files[0].name == "__init__.py":
            empty_engines.append(folder.name)
        else:
            implemented_engines.append(folder.name)
            
    print(f"Total Engine Modules: {len(engine_folders)}")
    print(f"Empty/Placeholder Modules ({len(empty_engines)}): {', '.join(empty_engines)}")
    print(f"Implemented Modules ({len(implemented_engines)}): {', '.join(implemented_engines)}")

def main():
    root = Path(r"C:\Users\sahil\Desktop\DevShield")
    backend_api = root / "backend" / "api"
    backend_engine = root / "backend" / "engine"
    
    analyze_backend(backend_api, backend_engine)
    analyze_engine(backend_engine)

if __name__ == "__main__":
    main()
