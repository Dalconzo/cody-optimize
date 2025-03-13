#!/usr/bin/env python3
import os
import sys
import json
import re

def extract_functions_and_classes(file_path):
    """
    Extract function and class names from a file based on its extension
    """
    print(f"\nAnalyzing file: {file_path}")
    
    # Get file extension to determine language
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    print(f"  File extension: {ext}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        print(f"  Successfully read file ({len(content)} bytes)")
            
        # Dictionary to store extracted items
        extracted = {
            "functions": [],
            "classes": [],
            "methods": [],
            "language": "unknown"
        }
        
        # Python
        if ext in ['.py']:
            print(f"  Detected language: Python")
            extracted["language"] = "python"
            
            # Extract functions
            print(f"  Searching for Python functions...")
            function_matches = re.finditer(r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(', content, re.MULTILINE)
            functions = [match.group(1) for match in function_matches]
            extracted["functions"] = functions
            print(f"  Found {len(functions)} functions: {', '.join(functions) if functions else 'None'}")
            
            # Extract classes
            print(f"  Searching for Python classes...")
            class_matches = re.finditer(r'^\s*class\s+([a-zA-Z0-9_]+)\s*[\(:]', content, re.MULTILINE)
            classes = [match.group(1) for match in class_matches]
            extracted["classes"] = classes
            print(f"  Found {len(classes)} classes: {', '.join(classes) if classes else 'None'}")
        
        # JavaScript/TypeScript
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            lang_name = "JavaScript" if ext in ['.js', '.jsx'] else "TypeScript"
            print(f"  Detected language: {lang_name}")
            extracted["language"] = "javascript" if ext in ['.js', '.jsx'] else "typescript"
            
            # Extract functions
            print(f"  Searching for {lang_name} functions...")
            function_matches = re.finditer(r'function\s+([a-zA-Z0-9_$]+)\s*\(|^\s*(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(.*\)\s*=>', content, re.MULTILINE)
            functions = [match.group(1) or match.group(2) for match in function_matches if match.group(1) or match.group(2)]
            extracted["functions"] = functions
            print(f"  Found {len(functions)} functions: {', '.join(functions[:5]) + ('...' if len(functions) > 5 else '') if functions else 'None'}")
            
            # Extract classes
            print(f"  Searching for {lang_name} classes...")
            class_matches = re.finditer(r'class\s+([a-zA-Z0-9_$]+)', content, re.MULTILINE)
            classes = [match.group(1) for match in class_matches]
            extracted["classes"] = classes
            print(f"  Found {len(classes)} classes: {', '.join(classes) if classes else 'None'}")
            
            # Extract methods
            print(f"  Searching for {lang_name} methods...")
            method_matches = re.finditer(r'(?:async\s+)?([a-zA-Z0-9_$]+)\s*\([^)]*\)\s*{', content, re.MULTILINE)
            methods = [match.group(1) for match in method_matches if match.group(1) not in ['if', 'for', 'while', 'switch', 'catch']]
            extracted["methods"] = methods
            print(f"  Found {len(methods)} methods: {', '.join(methods[:5]) + ('...' if len(methods) > 5 else '') if methods else 'None'}")
            
        # Java/C#
        elif ext in ['.java', '.cs']:
            lang_name = "Java" if ext == '.java' else "C#"
            print(f"  Detected language: {lang_name}")
            extracted["language"] = "java" if ext == '.java' else "csharp"
            
            # Extract classes and interfaces
            print(f"  Searching for {lang_name} classes and interfaces...")
            class_matches = re.finditer(r'(?:public|private|protected)?\s+(?:abstract|final)?\s*(?:class|interface)\s+([a-zA-Z0-9_$]+)', content, re.MULTILINE)
            classes = [match.group(1) for match in class_matches]
            extracted["classes"] = classes
            print(f"  Found {len(classes)} classes/interfaces: {', '.join(classes) if classes else 'None'}")
            
            # Extract methods
            print(f"  Searching for {lang_name} methods...")
            method_matches = re.finditer(r'(?:public|private|protected)?\s+(?:static|final|abstract)?\s+[a-zA-Z0-9_$<>]+\s+([a-zA-Z0-9_$]+)\s*\([^)]*\)', content, re.MULTILINE)
            methods = [match.group(1) for match in method_matches]
            extracted["methods"] = methods
            print(f"  Found {len(methods)} methods: {', '.join(methods[:5]) + ('...' if len(methods) > 5 else '') if methods else 'None'}")
        
        # C/C++
        elif ext in ['.c', '.cpp', '.cc', '.h', '.hpp']:
            lang_name = "C" if ext in ['.c', '.h'] else "C++"
            print(f"  Detected language: {lang_name}")
            extracted["language"] = "c" if ext in ['.c', '.h'] else "cpp"
            
            # Extract functions
            print(f"  Searching for {lang_name} functions...")
            function_matches = re.finditer(r'(?:[\w:]+\s+)+(\w+)\s*\([^)]*\)\s*(?:const)?\s*(?:{|;)', content, re.MULTILINE)
            functions = [match.group(1) for match in function_matches if match.group(1) not in ['if', 'for', 'while', 'switch', 'catch']]
            extracted["functions"] = functions
            print(f"  Found {len(functions)} functions: {', '.join(functions[:5]) + ('...' if len(functions) > 5 else '') if functions else 'None'}")
            
            # Extract classes (C++ only)
            if ext in ['.cpp', '.cc', '.hpp']:
                print(f"  Searching for C++ classes...")
                class_matches = re.finditer(r'class\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
                classes = [match.group(1) for match in class_matches]
                extracted["classes"] = classes
                print(f"  Found {len(classes)} classes: {', '.join(classes) if classes else 'None'}")
        else:
            print(f"  Unsupported file extension: {ext} - skipping detailed analysis")
        
        # Remove duplicates while preserving order
        functions_dedup = list(dict.fromkeys(extracted["functions"]))
        classes_dedup = list(dict.fromkeys(extracted["classes"]))
        methods_dedup = list(dict.fromkeys(extracted["methods"]))
        
        if len(functions_dedup) != len(extracted["functions"]):
            print(f"  Removed {len(extracted['functions']) - len(functions_dedup)} duplicate functions")
        if len(classes_dedup) != len(extracted["classes"]):
            print(f"  Removed {len(extracted['classes']) - len(classes_dedup)} duplicate classes")
        if len(methods_dedup) != len(extracted["methods"]):
            print(f"  Removed {len(extracted['methods']) - len(methods_dedup)} duplicate methods")
            
        extracted["functions"] = functions_dedup
        extracted["classes"] = classes_dedup
        extracted["methods"] = methods_dedup
        
        print(f"  Analysis complete: found {len(extracted['functions'])} functions, {len(extracted['classes'])} classes, {len(extracted['methods'])} methods")
        return extracted
        
    except Exception as e:
        print(f"  ERROR: Failed to analyze file: {type(e).__name__}: {str(e)}")
        return {
            "functions": [],
            "classes": [],
            "methods": [],
            "language": "unknown",
            "error": f"{type(e).__name__}: {str(e)}"
        }

def generate_folder_structure(path, ignore_folders=None):
    """
    Recursively generate a dictionary representing the folder structure
    
    Args:
        path: Path to the directory or file
        ignore_folders: List of folder names to ignore
    """
    if ignore_folders is None:
        ignore_folders = []
    
    print(f"Processing: {path}")
    structure = {}
    
    # Get the base name of the path
    name = os.path.basename(os.path.normpath(path))
    
    # Skip if this folder should be ignored
    if os.path.isdir(path) and name in ignore_folders:
        print(f"  Skipping ignored folder: {name}")
        return None
    
    if os.path.isdir(path):
        print(f"  Directory: {name}")
        structure["type"] = "directory"
        structure["name"] = name
        structure["children"] = []
        
        try:
            # List all items in the directory
            items = sorted(os.listdir(path))
            print(f"  Found {len(items)} items in directory")
            for item in items:
                # Skip hidden files and directories
                if item.startswith('.'):
                    print(f"  Skipping hidden item: {item}")
                    continue
                
                item_path = os.path.join(path, item)
                child_structure = generate_folder_structure(item_path, ignore_folders)
                if child_structure is not None:
                    structure["children"].append(child_structure)
        except PermissionError as e:
            print(f"  ERROR: Permission denied for {path}: {str(e)}")
            structure["error"] = f"Permission denied: {str(e)}"
        except Exception as e:
            print(f"  ERROR: Failed to process directory {path}: {type(e).__name__}: {str(e)}")
            structure["error"] = f"{type(e).__name__}: {str(e)}"
    else:
        print(f"  File: {name}")
        structure["type"] = "file"
        structure["name"] = name
        
        # Extract function and class information instead of full content
        try:
            structure["definitions"] = extract_functions_and_classes(path)
        except Exception as e:
            print(f"  ERROR: Failed to extract definitions: {type(e).__name__}: {str(e)}")
            structure["definitions"] = {
                "error": f"Failed to extract definitions: {type(e).__name__}: {str(e)}"
            }
    
    return structure

def main():
    print("\n===== FUNCTION AND CLASS EXTRACTOR =====")
    print(f"Command line arguments: {sys.argv}")
    
    if len(sys.argv) < 2:
        print("\nUsage: python function_class_extractor.py <folder_path> [ignore_folders]")
        print("       where ignore_folders is a comma-separated list of folder names to ignore")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    print(f"\nTarget folder: {folder_path}")
    
    # Parse ignore folders if provided
    ignore_folders = []
    if len(sys.argv) > 2:
        ignore_folders = [folder.strip() for folder in sys.argv[2].split(',')]
        print(f"Ignoring folders: {', '.join(ignore_folders)}")
    
    if not os.path.exists(folder_path):
        print(f"\nERROR: The path '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"\nERROR: '{folder_path}' is not a directory.")
        sys.exit(1)

    # Create outputs directory if it doesn't exist
    outputs_dir = "outputs"
    print(f"\nSetting up output directory: {outputs_dir}")
    if not os.path.exists(outputs_dir):
        try:
            os.makedirs(outputs_dir)
            print(f"Created directory: {outputs_dir}")
        except Exception as e:
            print(f"ERROR: Failed to create outputs directory: {type(e).__name__}: {str(e)}")
            print("Saving to current directory instead.")
            outputs_dir = "."
    else:
        print(f"Using existing directory: {outputs_dir}")

    # Generate folder structure
    print("\n===== GENERATING FOLDER STRUCTURE =====")
    print("Starting analysis of directory structure and file contents...")
    structure = generate_folder_structure(folder_path, ignore_folders)
    
    # Get the folder name for the output file
    folder_name = os.path.basename(os.path.normpath(folder_path))
    output_file = os.path.join(outputs_dir, f"{folder_name}_definitions.json")
    
    # Write to file
    print(f"\n===== SAVING RESULTS =====")
    print(f"Writing results to: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        file_size = os.path.getsize(output_file)
        print(f"Successfully saved output file ({file_size} bytes)")
    except Exception as e:
        print(f"ERROR: Failed to write output file: {type(e).__name__}: {str(e)}")
    
    print(f"\n===== EXTRACTION COMPLETE =====")
    print(f"Function and class definitions have been saved to '{output_file}'")

if __name__ == "__main__":
    main()
