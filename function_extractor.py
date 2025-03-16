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
            
            # Extract functions with preceding comments
            print(f"  Searching for Python functions...")
            # First, find all functions
            function_matches = list(re.finditer(r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(', content, re.MULTILINE))
            functions = []
            
            for match in function_matches:
                func_name = match.group(1)
                func_start_pos = match.start()
                
                # Look for comments before the function
                # This handles both # comments and docstrings
                comment = ""
                
                # Look for # comments before the function
                line_start = content.rfind('\n', 0, func_start_pos) + 1
                if line_start > 0:
                    # Look for consecutive # comment lines before the function
                    comment_lines = []
                    current_pos = line_start - 2  # Start from the line before
                    
                    while current_pos > 0:
                        prev_line_start = content.rfind('\n', 0, current_pos) + 1
                        prev_line = content[prev_line_start:current_pos+1].strip()
                        
                        if prev_line.startswith('#'):
                            comment_lines.insert(0, prev_line)
                            current_pos = prev_line_start - 1
                        else:
                            break
                    
                    if comment_lines:
                        comment = '\n'.join(comment_lines)
                
                # Look for docstring after the function definition
                func_def_end = content.find(':', func_start_pos) + 1
                next_line_start = content.find('\n', func_def_end) + 1
                
                if next_line_start > 0 and next_line_start < len(content):
                    next_line = content[next_line_start:content.find('\n', next_line_start)].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        # Found a docstring, extract it
                        docstring_start = next_line_start + content[next_line_start:].find(next_line)
                        docstring_delimiter = next_line[:3]
                        docstring_end = content.find(docstring_delimiter, docstring_start + 3)
                        
                        if docstring_end > docstring_start:
                            docstring = content[docstring_start:docstring_end + 3]
                            if comment:
                                comment += "\n\n" + docstring
                            else:
                                comment = docstring
                
                functions.append({"name": func_name, "comment": comment.strip() if comment else None})
            
            extracted["functions"] = functions
            print(f"  Found {len(functions)} functions")
            
            # Extract classes with preceding comments
            print(f"  Searching for Python classes...")
            class_matches = list(re.finditer(r'^\s*class\s+([a-zA-Z0-9_]+)\s*[\(:]', content, re.MULTILINE))
            classes = []
            
            for match in class_matches:
                class_name = match.group(1)
                class_start_pos = match.start()
                
                # Look for comments before the class
                comment = ""
                
                # Look for # comments before the class
                line_start = content.rfind('\n', 0, class_start_pos) + 1
                if line_start > 0:
                    # Look for consecutive # comment lines before the class
                    comment_lines = []
                    current_pos = line_start - 2  # Start from the line before
                    
                    while current_pos > 0:
                        prev_line_start = content.rfind('\n', 0, current_pos) + 1
                        prev_line = content[prev_line_start:current_pos+1].strip()
                        
                        if prev_line.startswith('#'):
                            comment_lines.insert(0, prev_line)
                            current_pos = prev_line_start - 1
                        else:
                            break
                    
                    if comment_lines:
                        comment = '\n'.join(comment_lines)
                
                # Look for docstring after the class definition
                class_def_end = content.find(':', class_start_pos) + 1
                next_line_start = content.find('\n', class_def_end) + 1
                
                if next_line_start > 0 and next_line_start < len(content):
                    next_line = content[next_line_start:content.find('\n', next_line_start)].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        # Found a docstring, extract it
                        docstring_start = next_line_start + content[next_line_start:].find(next_line)
                        docstring_delimiter = next_line[:3]
                        docstring_end = content.find(docstring_delimiter, docstring_start + 3)
                        
                        if docstring_end > docstring_start:
                            docstring = content[docstring_start:docstring_end + 3]
                            if comment:
                                comment += "\n\n" + docstring
                            else:
                                comment = docstring
                
                classes.append({"name": class_name, "comment": comment.strip() if comment else None})
            
            extracted["classes"] = classes
            print(f"  Found {len(classes)} classes")
        
        # JavaScript/TypeScript
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            lang_name = "JavaScript" if ext in ['.js', '.jsx'] else "TypeScript"
            print(f"  Detected language: {lang_name}")
            extracted["language"] = "javascript" if ext in ['.js', '.jsx'] else "typescript"
            
            # Extract functions with preceding comments
            print(f"  Searching for {lang_name} functions...")
            
            # Find all functions (both regular and arrow functions)
            function_patterns = [
                r'function\s+([a-zA-Z0-9_$]+)\s*\(',  # function name()
                r'^\s*(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(.*\)\s*=>'  # const name = () =>
            ]
            
            functions = []
            
            for pattern in function_patterns:
                function_matches = list(re.finditer(pattern, content, re.MULTILINE))
                
                for match in function_matches:
                    func_name = match.group(1)
                    func_start_pos = match.start()
                    
                    # Look for comments before the function
                    comment = ""
                    
                    # Look for // comments before the function
                    line_start = content.rfind('\n', 0, func_start_pos) + 1
                    if line_start > 0:
                        # Look for consecutive // comment lines before the function
                        comment_lines = []
                        current_pos = line_start - 2  # Start from the line before
                        
                        while current_pos > 0:
                            prev_line_start = content.rfind('\n', 0, current_pos) + 1
                            prev_line = content[prev_line_start:current_pos+1].strip()
                            
                            if prev_line.startswith('//'):
                                comment_lines.insert(0, prev_line)
                                current_pos = prev_line_start - 1
                            else:
                                break
                        
                        if comment_lines:
                            comment = '\n'.join(comment_lines)
                    
                    # Look for /* */ comments before the function
                    if not comment:
                        comment_end = func_start_pos
                        while comment_end > 0 and content[comment_end-1].isspace():
                            comment_end -= 1
                        
                        if comment_end > 0:
                            comment_start = content.rfind('/*', 0, comment_end)
                            if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                                comment_end = content.find('*/', comment_start) + 2
                                comment = content[comment_start:comment_end]
                    
                    # Look for JSDoc comments (/** */)
                    if not comment:
                        comment_end = func_start_pos
                        while comment_end > 0 and content[comment_end-1].isspace():
                            comment_end -= 1
                        
                        if comment_end > 0:
                            comment_start = content.rfind('/**', 0, comment_end)
                            if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                                comment_end = content.find('*/', comment_start) + 2
                                comment = content[comment_start:comment_end]
                    
                    functions.append({"name": func_name, "comment": comment.strip() if comment else None})
            
            extracted["functions"] = functions
            print(f"  Found {len(functions)} functions")
            
            # Extract classes with preceding comments
            print(f"  Searching for {lang_name} classes...")
            class_matches = list(re.finditer(r'class\s+([a-zA-Z0-9_$]+)', content, re.MULTILINE))
            classes = []
            
            for match in class_matches:
                class_name = match.group(1)
                class_start_pos = match.start()
                
                # Look for comments before the class
                comment = ""
                
                # Look for // comments before the class
                line_start = content.rfind('\n', 0, class_start_pos) + 1
                if line_start > 0:
                    # Look for consecutive // comment lines before the class
                    comment_lines = []
                    current_pos = line_start - 2  # Start from the line before
                    
                    while current_pos > 0:
                        prev_line_start = content.rfind('\n', 0, current_pos) + 1
                        prev_line = content[prev_line_start:current_pos+1].strip()
                        
                        if prev_line.startswith('//'):
                            comment_lines.insert(0, prev_line)
                            current_pos = prev_line_start - 1
                        else:
                            break
                    
                    if comment_lines:
                        comment = '\n'.join(comment_lines)
                
                # Look for /* */ comments before the class
                if not comment:
                    comment_end = class_start_pos
                    while comment_end > 0 and content[comment_end-1].isspace():
                        comment_end -= 1
                    
                    if comment_end > 0:
                        comment_start = content.rfind('/*', 0, comment_end)
                        if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                            comment_end = content.find('*/', comment_start) + 2
                            comment = content[comment_start:comment_end]
                
                # Look for JSDoc comments (/** */)
                if not comment:
                    comment_end = class_start_pos
                    while comment_end > 0 and content[comment_end-1].isspace():
                        comment_end -= 1
                    
                    if comment_end > 0:
                        comment_start = content.rfind('/**', 0, comment_end)
                        if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                            comment_end = content.find('*/', comment_start) + 2
                            comment = content[comment_start:comment_end]
                
                classes.append({"name": class_name, "comment": comment.strip() if comment else None})
            
            extracted["classes"] = classes
            print(f"  Found {len(classes)} classes")
            
            # Extract methods with preceding comments
            print(f"  Searching for {lang_name} methods...")
            method_matches = list(re.finditer(r'(?:async\s+)?([a-zA-Z0-9_$]+)\s*\([^)]*\)\s*{', content, re.MULTILINE))
            methods = []
            
            for match in method_matches:
                method_name = match.group(1)
                if method_name not in ['if', 'for', 'while', 'switch', 'catch']:
                    method_start_pos = match.start()
                    
                    # Look for comments before the method
                    comment = ""
                    
                    # Look for // comments before the method
                    line_start = content.rfind('\n', 0, method_start_pos) + 1
                    if line_start > 0:
                        # Look for consecutive // comment lines before the method
                        comment_lines = []
                        current_pos = line_start - 2  # Start from the line before
                        
                        while current_pos > 0:
                            prev_line_start = content.rfind('\n', 0, current_pos) + 1
                            prev_line = content[prev_line_start:current_pos+1].strip()
                            
                            if prev_line.startswith('//'):
                                comment_lines.insert(0, prev_line)
                                current_pos = prev_line_start - 1
                            else:
                                break
                        
                        if comment_lines:
                            comment = '\n'.join(comment_lines)
                    
                    # Look for /* */ comments before the method
                    if not comment:
                        comment_end = method_start_pos
                        while comment_end > 0 and content[comment_end-1].isspace():
                            comment_end -= 1
                        
                        if comment_end > 0:
                            comment_start = content.rfind('/*', 0, comment_end)
                            if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                                comment_end = content.find('*/', comment_start) + 2
                                comment = content[comment_start:comment_end]
                    
                    methods.append({"name": method_name, "comment": comment.strip() if comment else None})
            
            extracted["methods"] = methods
            print(f"  Found {len(methods)} methods")
            
        # Java/C#
        elif ext in ['.java', '.cs']:
            lang_name = "Java" if ext == '.java' else "C#"
            print(f"  Detected language: {lang_name}")
            extracted["language"] = "java" if ext == '.java' else "csharp"
            
            # Extract classes and interfaces with preceding comments
            print(f"  Searching for {lang_name} classes and interfaces...")
            class_matches = list(re.finditer(r'(?:public|private|protected)?\s+(?:abstract|final)?\s*(?:class|interface)\s+([a-zA-Z0-9_$]+)', content, re.MULTILINE))
            classes = []
            
            for match in class_matches:
                class_name = match.group(1)
                class_start_pos = match.start()
                
                # Look for comments before the class
                comment = ""
                
                # Look for // comments before the class
                line_start = content.rfind('\n', 0, class_start_pos) + 1
                if line_start > 0:
                    # Look for consecutive // comment lines before the class
                    comment_lines = []
                    current_pos = line_start - 2  # Start from the line before
                    
                    while current_pos > 0:
                        prev_line_start = content.rfind('\n', 0, current_pos) + 1
                        prev_line = content[prev_line_start:current_pos+1].strip()
                        
                        if prev_line.startswith('//'):
                            comment_lines.insert(0, prev_line)
                            current_pos = prev_line_start - 1
                        else:
                            break
                    
                    if comment_lines:
                        comment = '\n'.join(comment_lines)
                
                # Look for /* */ comments before the class
                if not comment:
                    comment_end = class_start_pos
                    while comment_end > 0 and content[comment_end-1].isspace():
                        comment_end -= 1
                    
                    if comment_end > 0:
                        comment_start = content.rfind('/*', 0, comment_end)
                        if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                            comment_end = content.find('*/', comment_start) + 2
                            comment = content[comment_start:comment_end]
                
                # Look for Javadoc comments (/** */)
                if not comment:
                    comment_end = class_start_pos
                    while comment_end > 0 and content[comment_end-1].isspace():
                        comment_end -= 1
                    
                    if comment_end > 0:
                        comment_start = content.rfind('/**', 0, comment_end)
                        if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                            comment_end = content.find('*/', comment_start) + 2
                            comment = content[comment_start:comment_end]
                
                classes.append({"name": class_name, "comment": comment.strip() if comment else None})
            
            extracted["classes"] = classes
            print(f"  Found {len(classes)} classes/interfaces")
            
            # Extract methods with preceding comments
            print(f"  Searching for {lang_name} methods...")
            method_matches = list(re.finditer(r'(?:public|private|protected)?\s+(?:static|final|abstract)?\s+[a-zA-Z0-9_$<>]+\s+([a-zA-Z0-9_$]+)\s*\([^)]*\)', content, re.MULTILINE))
            methods = []
            
            for match in method_matches:
                method_name = match.group(1)
                method_start_pos = match.start()
                
                # Look for comments before the method
                comment = ""
                
                # Look for // comments before the method
                line_start = content.rfind('\n', 0, method_start_pos) + 1
                if line_start > 0:
                    # Look for consecutive // comment lines before the method
                    comment_lines = []
                    current_pos = line_start - 2  # Start from the line before
                    
                    while current_pos > 0:
                        prev_line_start = content.rfind('\n', 0, current_pos) + 1
                        prev_line = content[prev_line_start:current_pos+1].strip()
                        
                        if prev_line.startswith('//'):
                            comment_lines.insert(0, prev_line)
                            current_pos = prev_line_start - 1
                        else:
                            break
                    
                    if comment_lines:
                        comment = '\n'.join(comment_lines)
                
                # Look for /* */ comments before the method
                if not comment:
                    comment_end = method_start_pos
                    while comment_end > 0 and content[comment_end-1].isspace():
                        comment_end -= 1
                    
                    if comment_end > 0:
                        comment_start = content.rfind('/*', 0, comment_end)
                        if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                            comment_end = content.find('*/', comment_start) + 2
                            comment = content[comment_start:comment_end]
                
                # Look for Javadoc comments (/** */)
                if not comment:
                    comment_end = method_start_pos
                    while comment_end > 0 and content[comment_end-1].isspace():
                        comment_end -= 1
                    
                    if comment_end > 0:
                        comment_start = content.rfind('/**', 0, comment_end)
                        if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                            comment_end = content.find('*/', comment_start) + 2
                            comment = content[comment_start:comment_end]
                
                methods.append({"name": method_name, "comment": comment.strip() if comment else None})
            
            extracted["methods"] = methods
            print(f"  Found {len(methods)} methods")
        
        # C/C++
        elif ext in ['.c', '.cpp', '.cc', '.h', '.hpp']:
            lang_name = "C" if ext in ['.c', '.h'] else "C++"
            print(f"  Detected language: {lang_name}")
            extracted["language"] = "c" if ext in ['.c', '.h'] else "cpp"
            
            # Extract functions with preceding comments
            print(f"  Searching for {lang_name} functions...")
            function_matches = list(re.finditer(r'(?:[\w:]+\s+)+(\w+)\s*\([^)]*\)\s*(?:const)?\s*(?:{|;)', content, re.MULTILINE))
            functions = []
            
            for match in function_matches:
                func_name = match.group(1)
                if func_name not in ['if', 'for', 'while', 'switch', 'catch']:
                    func_start_pos = match.start()
                    
                    # Look for comments before the function
                    comment = ""
                    
                    # Look for // comments before the function
                    line_start = content.rfind('\n', 0, func_start_pos) + 1
                    if line_start > 0:
                        # Look for consecutive // comment lines before the function
                        comment_lines = []
                        current_pos = line_start - 2  # Start from the line before
                        
                        while current_pos > 0:
                            prev_line_start = content.rfind('\n', 0, current_pos) + 1
                            prev_line = content[prev_line_start:current_pos+1].strip()
                            
                            if prev_line.startswith('//'):
                                comment_lines.insert(0, prev_line)
                                current_pos = prev_line_start - 1
                            else:
                                break
                        
                        if comment_lines:
                            comment = '\n'.join(comment_lines)
                    
                    # Look for /* */ comments before the function
                    if not comment:
                        comment_end = func_start_pos
                        while comment_end > 0 and content[comment_end-1].isspace():
                            comment_end -= 1
                        
                        if comment_end > 0:
                            comment_start = content.rfind('/*', 0, comment_end)
                            if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                                comment_end = content.find('*/', comment_start) + 2
                                comment = content[comment_start:comment_end]
                    
                    functions.append({"name": func_name, "comment": comment.strip() if comment else None})
            
            extracted["functions"] = functions
            print(f"  Found {len(functions)} functions")
            
            # Extract classes (C++ only) with preceding comments
            if ext in ['.cpp', '.cc', '.hpp']:
                print(f"  Searching for C++ classes...")
                class_matches = list(re.finditer(r'class\s+([a-zA-Z0-9_]+)', content, re.MULTILINE))
                classes = []
                
                for match in class_matches:
                    class_name = match.group(1)
                    class_start_pos = match.start()
                    
                    # Look for comments before the class
                    comment = ""
                    
                    # Look for // comments before the class
                    line_start = content.rfind('\n', 0, class_start_pos) + 1
                    if line_start > 0:
                        # Look for consecutive // comment lines before the class
                        comment_lines = []
                        current_pos = line_start - 2  # Start from the line before
                        
                        while current_pos > 0:
                            prev_line_start = content.rfind('\n', 0, current_pos) + 1
                            prev_line = content[prev_line_start:current_pos+1].strip()
                            
                            if prev_line.startswith('//'):
                                comment_lines.insert(0, prev_line)
                                current_pos = prev_line_start - 1
                            else:
                                break
                        
                        if comment_lines:
                            comment = '\n'.join(comment_lines)
                    
                    # Look for /* */ comments before the class
                    if not comment:
                        comment_end = class_start_pos
                        while comment_end > 0 and content[comment_end-1].isspace():
                            comment_end -= 1
                        
                        if comment_end > 0:
                            comment_start = content.rfind('/*', 0, comment_end)
                            if comment_start >= 0 and content.find('*/', comment_start, comment_end) > comment_start:
                                comment_end = content.find('*/', comment_start) + 2
                                comment = content[comment_start:comment_end]
                    
                    classes.append({"name": class_name, "comment": comment.strip() if comment else None})
                
                extracted["classes"] = classes
                print(f"  Found {len(classes)} classes")
        else:
            print(f"  Unsupported file extension: {ext} - skipping detailed analysis")
        
        # Remove duplicates while preserving order
        functions_dedup = []
        seen_functions = set()
        for func in extracted["functions"]:
            if func["name"] not in seen_functions:
                seen_functions.add(func["name"])
                functions_dedup.append(func)
        
        classes_dedup = []
        seen_classes = set()
        for cls in extracted["classes"]:
            if cls["name"] not in seen_classes:
                seen_classes.add(cls["name"])
                classes_dedup.append(cls)
        
        methods_dedup = []
        seen_methods = set()
        for method in extracted["methods"]:
            if method["name"] not in seen_methods:
                seen_methods.add(method["name"])
                methods_dedup.append(method)
        
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
    
    #print(f"Processing: {path}")
    structure = {}
    
    # Get the base name of the path
    name = os.path.basename(os.path.normpath(path))
    
    # Skip if this folder should be ignored
    if os.path.isdir(path) and name in ignore_folders:
        #print(f"  Skipping ignored folder: {name}")
        return None
    
    if os.path.isdir(path):
        #print(f"  Directory: {name}")
        structure["type"] = "directory"
        structure["name"] = name
        structure["children"] = []
        
        try:
            # List all items in the directory
            items = sorted(os.listdir(path))
            #print(f"  Found {len(items)} items in directory")
            for item in items:
                # Skip hidden files and directories
                if item.startswith('.'):
                    #print(f"  Skipping hidden item: {item}")
                    continue
                
                item_path = os.path.join(path, item)
                child_structure = generate_folder_structure(item_path, ignore_folders)
                if child_structure is not None:
                    structure["children"].append(child_structure)
        except PermissionError as e:
            #print(f"  ERROR: Permission denied for {path}: {str(e)}")
            structure["error"] = f"Permission denied: {str(e)}"
        except Exception as e:
            #print(f"  ERROR: Failed to process directory {path}: {type(e).__name__}: {str(e)}")
            structure["error"] = f"{type(e).__name__}: {str(e)}"
    else:
        #print(f"  File: {name}")
        structure["type"] = "file"
        structure["name"] = name
        
        # Extract function and class information instead of full content
        try:
            structure["definitions"] = extract_functions_and_classes(path)
        except Exception as e:
            #print(f"  ERROR: Failed to extract definitions: {type(e).__name__}: {str(e)}")
            structure["definitions"] = {
                "error": f"Failed to extract definitions: {type(e).__name__}: {str(e)}"
            }
    
    return structure

def main():
    #print("\n===== FUNCTION AND CLASS EXTRACTOR =====")
    #print(f"Command line arguments: {sys.argv}")
    
    if len(sys.argv) < 2:
        #print("\nUsage: python function_class_extractor.py <folder_path> [ignore_folders]")
        #print("       where ignore_folders is a comma-separated list of folder names to ignore")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    #print(f"\nTarget folder: {folder_path}")
    
    # Parse ignore folders if provided
    ignore_folders = []
    if len(sys.argv) > 2:
        ignore_folders = [folder.strip() for folder in sys.argv[2].split(',')]
        #print(f"Ignoring folders: {', '.join(ignore_folders)}")
    
    if not os.path.exists(folder_path):
        #print(f"\nERROR: The path '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        #print(f"\nERROR: '{folder_path}' is not a directory.")
        sys.exit(1)

    # Create outputs directory if it doesn't exist
    outputs_dir = "outputs"
    #print(f"\nSetting up output directory: {outputs_dir}")
    if not os.path.exists(outputs_dir):
        try:
            os.makedirs(outputs_dir)
            #print(f"Created directory: {outputs_dir}")
        except Exception as e:
            #print(f"ERROR: Failed to create outputs directory: {type(e).__name__}: {str(e)}")
            #print("Saving to current directory instead.")
            outputs_dir = "."
    else:
        #print(f"Using existing directory: {outputs_dir}")
        pass

    # Generate folder structure
    #print("\n===== GENERATING FOLDER STRUCTURE =====")
    #print("Starting analysis of directory structure and file contents...")
    structure = generate_folder_structure(folder_path, ignore_folders)
    
    # Get the folder name for the output file
    folder_name = os.path.basename(os.path.normpath(folder_path))
    output_file = os.path.join(outputs_dir, f"{folder_name}_definitions.json")
    
    # Write to file
    #print(f"\n===== SAVING RESULTS =====")
    #print(f"Writing results to: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        file_size = os.path.getsize(output_file)
        #print(f"Successfully saved output file ({file_size} bytes)")
    except Exception as e:
        #print(f"ERROR: Failed to write output file: {type(e).__name__}: {str(e)}")
        pass
    
    #print(f"\n===== EXTRACTION COMPLETE =====")
    #print(f"Function and class definitions have been saved to '{output_file}'")

if __name__ == "__main__":
    main()
