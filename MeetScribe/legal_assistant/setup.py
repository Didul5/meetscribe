"""
Setup script to create directory structure and empty __init__.py files.
"""
import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create the directory structure for the legal assistant application."""
    # Define the base directory
    base_dir = Path("legal_assistant")
    
    # Create the base directory if it doesn't exist
    if not base_dir.exists():
        base_dir.mkdir()
        print(f"Created directory: {base_dir}")
    
    # Define subdirectories
    subdirs = ["services", "models", "ui", "utils"]
    
    # Create subdirectories and __init__.py files
    for subdir in subdirs:
        subdir_path = base_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir()
            print(f"Created directory: {subdir_path}")
        
        # Create __init__.py in each subdirectory
        init_file = subdir_path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"Created file: {init_file}")
    
    print("Directory structure created successfully!")
    print(f"Project is set up at: {os.path.abspath(base_dir)}")

def create_empty_files():
    """Create any other necessary empty files."""
    # This could be extended to create other starter files if needed
    pass

if __name__ == "__main__":
    print("Setting up LegalMind Assistant project...")
    create_directory_structure()
    create_empty_files()
    print("\nSetup complete! To start developing, copy the provided code files into the appropriate directories.")
    print("Then run: cd legal_assistant && streamlit run app.py")