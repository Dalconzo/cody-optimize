#!/usr/bin/env python3
import os
import json
import sys

def read_file_content(file_path):
    """
    Safely read and return file content
    """
    try:
        # First try to read as text
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except (UnicodeDecodeError, PermissionError, IsADirectoryError, FileNotFoundError):
        try:
            # Try binary files but convert to string with limited chars
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Only read beginning to identify binary
                if b'\x00' in content:
                    return "[Binary file - content not displayed]"
                else:
                    # It seems like text, try full read with replace for problematic chars
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        return f.read()
        except Exception as e:
            return f"[Error reading file: {str(e)}]"

def generate_folder_structure(path, ignore_folders=None, max_file_size=1024*1024):
    """
    Recursively generate a dictionary representing the folder structure
    
    Args:
        path: Path to the directory or file
        ignore_folders: List of folder names to ignore
        max_file_size: Maximum file size to read content from (in bytes)
    """
    if ignore_folders is None:
        ignore_folders = []
    
    structure = {}
    
    # Get the base name of the path
    name = os.path.basename(os.path.normpath(path))
    
    # Skip if this folder should be ignored
    if os.path.isdir(path) and name in ignore_folders:
        return None
    
    if os.path.isdir(path):
        structure["type"] = "directory"
        structure["name"] = name
        structure["children"] = []
        
        try:
            # List all items in the directory
            for item in sorted(os.listdir(path)):
                # Skip hidden files and directories
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                child_structure = generate_folder_structure(item_path, ignore_folders, max_file_size)
                if child_structure is not None:
                    structure["children"].append(child_structure)
        except PermissionError:
            structure["error"] = "Permission denied"
    else:
        structure["type"] = "file"
        structure["name"] = name
        
        # Check file size before reading content
        try:
            file_size = os.path.getsize(path)
            if file_size <= max_file_size:
                structure["content"] = read_file_content(path)
            else:
                structure["content"] = f"[File too large to display: {file_size/1024/1024:.2f} MB]"
        except Exception as e:
            structure["content"] = f"[Error: {str(e)}]"
    
    return structure

def main():
    if len(sys.argv) < 2:
        print("Usage: python folder_structure_to_json.py <folder_path> [ignore_folders]")
        print("       where ignore_folders is a comma-separated list of folder names to ignore")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    # Parse ignore folders if provided
    ignore_folders = []
    if len(sys.argv) > 2:
        ignore_folders = [folder.strip() for folder in sys.argv[2].split(',')]
        print(f"Ignoring folders: {', '.join(ignore_folders)}")
    
    if not os.path.exists(folder_path):
        print(f"Error: The path '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)

    # Create outputs directory if it doesn't exist
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        try:
            os.makedirs(outputs_dir)
            print(f"Created directory: {outputs_dir}")
        except Exception as e:
            print(f"Error creating outputs directory: {str(e)}")
            print("Saving to current directory instead.")
            outputs_dir = "."

    
    # Generate folder structure
    print("Generating folder structure... This may take a while for large codebases.")
    structure = generate_folder_structure(folder_path, ignore_folders)
    
    # Get the folder name for the output file
    folder_name = os.path.basename(os.path.normpath(folder_path))
    output_file = os.path.join(outputs_dir, f"{folder_name}_structure.txt")
    
    # Write to file
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print(f"Folder structure with file contents has been saved to '{output_file}'")

if __name__ == "__main__":
    main()
