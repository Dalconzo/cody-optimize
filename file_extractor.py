#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

def read_file_content(file_path):
    """
    Safely read and return file content
    """
    print(f"Reading file: {file_path}")
    try:
        # First try to read as text
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            print(f"  Successfully read as text ({len(content)} characters)")
            return content
    except (UnicodeDecodeError, PermissionError, IsADirectoryError, FileNotFoundError) as e:
        print(f"  Initial read attempt failed: {type(e).__name__}: {e}")
        try:
            # Try binary files but convert to string with limited chars
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Only read beginning to identify binary
                if b'\x00' in content:
                    print(f"  Detected as binary file")
                    return "[Binary file - content not displayed]"
                else:
                    print(f"  Appears to be text, retrying with error replacement")
                    # It seems like text, try full read with replace for problematic chars
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                        print(f"  Successfully read with replacement ({len(content)} characters)")
                        return content
        except Exception as e:
            print(f"  Failed to read file: {type(e).__name__}: {e}")
            return f"[Error reading file: {str(e)}]"

def parse_content_with_line_numbers(content):
    """
    Convert content string to a dictionary with line numbers as keys
    """
    if content.startswith("[Binary file") or content.startswith("[Error"):
        # For binary or error cases, return as is
        return {"0": content}
    
    lines = content.split('\n')
    result = {}
    for i, line in enumerate(lines, 1):
        result[str(i)] = line
    
    return result

def find_specific_files(root_path, target_files, match_extension=True, ignore_folders=None, max_file_size=1024*1024):
    """
    Find all files with specific names in the directory structure
    """
    if ignore_folders is None:
        ignore_folders = []
    
    found_files = []
    files_checked = 0
    dirs_searched = 0
    
    print(f"Starting search in {root_path}")
    print(f"Looking for: {target_files}")
    print(f"Match extension: {match_extension}")
    print(f"Ignoring folders: {ignore_folders}")
    
    for root, dirs, files in os.walk(root_path):
        dirs_searched += 1
        if dirs_searched % 100 == 0:
            print(f"Searched {dirs_searched} directories, checked {files_checked} files, found {len(found_files)} matches so far...")
        
        # Remove ignored directories
        original_dirs_count = len(dirs)
        dirs[:] = [d for d in dirs if d not in ignore_folders and not d.startswith('.')]
        if len(dirs) < original_dirs_count:
            print(f"Skipping {original_dirs_count - len(dirs)} ignored/hidden directories in {root}")
        
        for file in files:
            files_checked += 1
            
            if file.startswith('.'):
                continue
                
            file_path = os.path.join(root, file)
            
            # Check if this file matches any of our target files
            is_match = False
            matching_pattern = None
            
            if match_extension:
                is_match = file in target_files
                if is_match:
                    matching_pattern = file
            else:
                # Match just the name part without extension
                file_name = os.path.splitext(file)[0]
                is_match = file_name in target_files
                if is_match:
                    matching_pattern = file_name
            
            if is_match:
                print(f"MATCH FOUND: {file_path} (matched pattern: {matching_pattern})")
                try:
                    file_size = os.path.getsize(file_path)
                    print(f"  File size: {file_size/1024:.2f} KB")
                    
                    if file_size <= max_file_size:
                        print(f"  Reading file content...")
                        content = read_file_content(file_path)
                        # Parse content into line-numbered format
                        content_with_lines = parse_content_with_line_numbers(content)
                        rel_path = os.path.relpath(file_path, root_path)
                        found_files.append({
                            "name": file,
                            "relative_path": rel_path,
                            "full_path": file_path,
                            "content": content_with_lines
                        })
                        print(f"  Added to extraction list: {rel_path} with {len(content_with_lines)} lines")
                    else:
                        print(f"  SKIPPED: File too large: {file_path} - {file_size/1024/1024:.2f} MB")
                except Exception as e:
                    print(f"  ERROR: Failed to process file {file_path}: {type(e).__name__}: {e}")
    
    print(f"Search complete: checked {files_checked} files in {dirs_searched} directories")
    print(f"Found {len(found_files)} matching files")
    return found_files

def build_directory_structure(root_path, found_files, ignore_folders=None):
    """
    Build a hierarchical directory structure with the found files
    """
    if ignore_folders is None:
        ignore_folders = []
    
    print("Building directory structure...")
    
    # Initialize the root structure
    root_name = os.path.basename(os.path.normpath(root_path))
    structure = {
        "type": "directory",
        "name": root_name,
        "children": []
    }
    
    # Create a map to quickly find directories in our structure
    dir_map = {root_path: structure}
    
    # Process each found file
    for file_info in found_files:
        full_path = file_info["full_path"]
        rel_path = file_info["relative_path"]
        
        # Get directory path for this file
        dir_path = os.path.dirname(full_path)
        
        # Make sure all parent directories exist in our structure
        current_path = root_path
        path_parts = os.path.dirname(rel_path).split(os.sep)
        
        # Handle files in the root directory
        if path_parts == [""]:
            # This file is in the root directory, add it directly
            structure["children"].append({
                "type": "file",
                "name": file_info["name"],
                "content": file_info["content"]  # Fixed: Use the line-numbered content
            })
            print(f"Added file '{file_info['name']}' to root directory")
            continue
        
        # Create or find all parent directories
        for part in path_parts:
            if not part:  # Skip empty parts
                continue
                
            next_path = os.path.join(current_path, part)
            
            if next_path not in dir_map:
                # Create this directory in the structure
                parent_dir = dir_map[current_path]
                new_dir = {
                    "type": "directory",
                    "name": part,
                    "children": []
                }
                parent_dir["children"].append(new_dir)
                dir_map[next_path] = new_dir
                print(f"Created directory node: {part}")
            
            current_path = next_path
        
        # Now add the file to its parent directory
        parent_dir = dir_map[os.path.dirname(full_path)]
        parent_dir["children"].append({
            "type": "file",
            "name": file_info["name"],
            "content": file_info["content"]  # Fixed: Use the line-numbered content
        })
        print(f"Added file '{file_info['name']}' to '{os.path.basename(os.path.dirname(full_path))}'")
    
    print("Structure building complete")
    return structure

def main():
    if len(sys.argv) < 3:
        print("Usage: python find_and_extract_files.py <folder_path> <target_files> [options]")
        print("       <target_files> is a comma-separated list of filenames to find")
        print("Options:")
        print("  --ignore-folders=<folders>  Comma-separated list of folder names to ignore")
        print("  --ignore-extension          Match filenames without considering extensions")
        print("  --output-dir=<dir>          Custom output directory (default: 'outputs')")
        print("  --prefix=<prefix>           Custom prefix for output filename (default: 'extracted_')")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    target_files = [f.strip() for f in sys.argv[2].split(',')]
    
    print("\n=== CONFIGURATION ===")
    print(f"Root path: {folder_path}")
    print(f"Target files: {target_files}")
    
    # Default options
    ignore_folders = []
    match_extension = True
    outputs_dir = "outputs"
    prefix = "extracted_"
    
    # Parse additional options
    print("Command-line arguments:", sys.argv[3:])
    for arg in sys.argv[3:]:
        print(f"Processing argument: {arg}")
        if arg.startswith('--ignore-folders='):
            ignore_folders = [folder.strip() for folder in arg[17:].split(',')]
            print(f"Set ignore_folders to: {ignore_folders}")
        elif arg == '--ignore-extension':
            match_extension = False
            print("Set match_extension to: False")
        elif arg.startswith('--output-dir='):
            outputs_dir = arg[13:]
            print(f"Set outputs_dir to: {outputs_dir}")
        elif arg.startswith('--prefix='):
            prefix = arg[9:]
            print(f"Set prefix to: {prefix}")
    
    # Print configuration
    print("\n=== SEARCH PARAMETERS ===")
    print(f"Searching for files: {', '.join(target_files)}")
    print(f"Match including extension: {match_extension}")
    if ignore_folders:
        print(f"Ignoring folders: {', '.join(ignore_folders)}")
    
    if not os.path.exists(folder_path):
        print(f"ERROR: The path '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"ERROR: '{folder_path}' is not a directory.")
        sys.exit(1)

    # Create outputs directory if it doesn't exist
    print(f"\n=== OUTPUT SETUP ===")
    print(f"Output directory: {outputs_dir}")
    if not os.path.exists(outputs_dir):
        try:
            os.makedirs(outputs_dir)
            print(f"Created directory: {outputs_dir}")
        except Exception as e:
            print(f"ERROR: Failed to create outputs directory: {type(e).__name__}: {e}")
            print("Saving to current directory instead.")
            outputs_dir = "."
    else:
        print(f"Using existing directory: {outputs_dir}")
    
    # Find files
    print("\n=== STARTING FILE SEARCH ===")
    found_files = find_specific_files(folder_path, target_files, match_extension, ignore_folders)
    
    if not found_files:
        print("\nNo matching files found.")
        sys.exit(0)
    
    print(f"\n=== BUILDING STRUCTURED JSON WITH {len(found_files)} FILES ===")
    
    # Build structure
    structure = build_directory_structure(folder_path, found_files, ignore_folders)
    
    # Save structure to file
    folder_name = os.path.basename(os.path.normpath(folder_path))
    output_file = os.path.join(outputs_dir, f"{prefix}{folder_name}_structure.json")
    
    print(f"\n=== SAVING STRUCTURE TO {output_file} ===")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        print(f"SUCCESS: Saved structure with {len(found_files)} files to '{output_file}' ({os.path.getsize(output_file)} bytes)")
    except Exception as e:
        print(f"ERROR: Failed to write JSON file: {type(e).__name__}: {e}")
    
    print(f"\n=== EXTRACTION COMPLETE ===")

if __name__ == "__main__":
    main()
