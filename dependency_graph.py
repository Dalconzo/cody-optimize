#!/usr/bin/env python3
import os
import sys
import json
import re
from collections import defaultdict

def detect_language(file_path):
    """Determine file language based on extension"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.py':
        return 'python'
    elif ext in ['.js', '.jsx', '.ts', '.tsx']:
        return 'javascript'
    elif ext in ['.cpp', '.cc', '.hpp', '.h']:
        return 'cpp'
    return 'unknown'

def parse_dependencies(file_path, content, language):
    """Parse dependencies based on language"""
    if language == 'python':
        return parse_python_imports(content)
    elif language == 'javascript':
        return parse_javascript_imports(content, file_path)
    elif language == 'cpp':
        return parse_cpp_includes(content, file_path)
    return []

def parse_javascript_imports(content, file_path):
    """Parse JavaScript import statements"""
    imports = []
    
    # ES6 import patterns
    es6_patterns = [
        r'import\s+(\w+)\s+from\s+[\'"]([^\'"]*)[\'"](;)?',  # import module from 'path'
        r'import\s+\{\s*([^}]*)\s*\}\s+from\s+[\'"]([^\'"]*)[\'"](;)?',  # import { items } from 'path'
        r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]*)[\'"](;)?'  # import * as module from 'path'
    ]
    
    # CommonJS require
    require_pattern = r'(?:const|let|var)\s+(\w+|\{[^}]*\})\s*=\s*require\([\'"]([^\'"]*)[\'"]\)(;)?'
    
    # Process ES6 imports
    for pattern in es6_patterns:
        for match in re.finditer(pattern, content, re.MULTILINE):
            if pattern.startswith(r'import\s+\{\s*'):
                # import { x, y } from 'module'
                items = [item.strip() for item in match.group(1).split(',')]
                module_path = match.group(2)
                imports.append({
                    "type": "import_destructure",
                    "module": module_path,
                    "items": items
                })
            elif pattern.startswith(r'import\s+\*'):
                # import * as x from 'module'
                alias = match.group(1)
                module_path = match.group(2)
                imports.append({
                    "type": "import_namespace",
                    "module": module_path,
                    "alias": alias
                })
            else:
                # import x from 'module'
                module_name = match.group(1)
                module_path = match.group(2)
                imports.append({
                    "type": "import_default",
                    "module": module_path,
                    "name": module_name
                })
    
    # Process CommonJS requires
    for match in re.finditer(require_pattern, content, re.MULTILINE):
        variable = match.group(1)
        module_path = match.group(2)
        
        if variable.startswith('{'):
            # const { x, y } = require('module')
            items = [item.strip() for item in variable[1:-1].split(',')]
            imports.append({
                "type": "require_destructure",
                "module": module_path,
                "items": items
            })
        else:
            # const x = require('module')
            imports.append({
                "type": "require",
                "module": module_path,
                "name": variable
            })
    
    return imports

def parse_cpp_includes(content, file_path):
    """Parse C++ include statements"""
    includes = []
    
    # Standard include patterns
    system_include_pattern = r'#\s*include\s*<([^>]*)>'  # #include <header>
    local_include_pattern = r'#\s*include\s*"([^"]*)"'   # #include "header"
    
    # Find system includes
    for match in re.finditer(system_include_pattern, content, re.MULTILINE):
        header = match.group(1)
        includes.append({
            "type": "system_include",
            "header": header
        })
    
    # Find local includes
    for match in re.finditer(local_include_pattern, content, re.MULTILINE):
        header = match.group(1)
        includes.append({
            "type": "local_include",
            "header": header
        })
    
    # Also capture namespace usage for C++
    namespace_pattern = r'using\s+namespace\s+(\w+)(::(\w+))*\s*;'
    for match in re.finditer(namespace_pattern, content, re.MULTILINE):
        namespace = match.group(1)
        includes.append({
            "type": "namespace",
            "namespace": namespace
        })
    
    return includes

def parse_python_imports(content):
    """
    Parse import statements from Python files
    """
    # Dictionary to store imports
    imports = []
    
    # Look for standard imports
    import_patterns = [
        r'^\s*import\s+([\w\.]+)(?:\s+as\s+(\w+))?',  # import module [as name]
        r'^\s*from\s+([\w\.]+)\s+import\s+(.+)'       # from module import names
    ]
    
    for pattern in import_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            if pattern.startswith(r'^\s*import'):
                module = match.group(1)
                alias = match.group(2) if match.group(2) else None
                imports.append({
                    "type": "import",
                    "module": module,
                    "alias": alias
                })
            else:  # from ... import
                module = match.group(1)
                imported_items = match.group(2)
                
                # Handle multi-line imports and parentheses
                if '(' in imported_items and ')' not in imported_items:
                    # This is a multi-line import, we need to find the closing parenthesis
                    # For simplicity in this example, we'll just note it's a multi-line import
                    imports.append({
                        "type": "from_import",
                        "module": module,
                        "items": ["multi-line-import"]
                    })
                else:
                    # Clean up the imported items (handle parentheses and commas)
                    imported_items = imported_items.replace('(', '').replace(')', '')
                    items = []
                    
                    # Split by comma but handle "as" clauses
                    for item in imported_items.split(','):
                        item = item.strip()
                        if ' as ' in item:
                            name, alias = item.split(' as ')
                            items.append({"name": name.strip(), "alias": alias.strip()})
                        else:
                            items.append({"name": item, "alias": None})
                    
                    imports.append({
                        "type": "from_import",
                        "module": module,
                        "items": items
                    })
    
    return imports

def find_function_calls_by_language(content, language):
    """Find function calls based on language"""
    if language == 'python':
        return find_python_function_calls(content)
    elif language == 'javascript':
        return find_javascript_function_calls(content)
    elif language == 'cpp':
        return find_cpp_function_calls(content)
    return []

def find_javascript_function_calls(content):
    """Find JavaScript function calls"""
    # Handle method calls (obj.method()) and direct calls (func())
    function_call_pattern = r'(?:(\w+)\.)?(\w+)\s*\([^)]*\)'
    
    calls = []
    for match in re.finditer(function_call_pattern, content):
        obj = match.group(1)
        method = match.group(2)
        
        # Skip common JS keywords like if, for, while
        if method not in ['if', 'for', 'while', 'switch', 'catch']:
            if obj:
                calls.append(f"{obj}.{method}")
            else:
                calls.append(method)
    
    return list(dict.fromkeys(calls))

def find_cpp_function_calls(content):
    """Find C++ function calls"""
    # This is simplified - C++ parsing is complex
    # Handle namespaced calls (std::cout) and regular calls (func())
    function_call_pattern = r'(?:(\w+)::)?(\w+)\s*\([^;]*\)'
    
    calls = []
    for match in re.finditer(function_call_pattern, content):
        namespace = match.group(1)
        function = match.group(2)
        
        # Skip common C++ constructs 
        if function not in ['if', 'for', 'while', 'switch', 'catch']:
            if namespace:
                calls.append(f"{namespace}::{function}")
            else:
                calls.append(function)
    
    return list(dict.fromkeys(calls))

def find_python_function_calls(content):
    """Find function calls in Python code"""
    # Basic pattern for function calls: name(args)
    # Also captures method calls: object.method(args)
    function_call_pattern = r'([\w\.]+)\s*\('
    
    calls = []
    matches = re.finditer(function_call_pattern, content)
    for match in matches:
        func_name = match.group(1)
        
        # Exclude common Python keywords and built-ins that match our pattern
        if func_name.split('.')[-1] not in ['if', 'for', 'while', 'with', 'print', 'elif', 'else']:
            calls.append(func_name)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(calls))

def analyze_file(file_path):
    """
    Analyze a single file for dependencies
    """
    print(f"Analyzing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        language = detect_language(file_path)
        
        file_info = {
            "path": file_path,
            "imports": parse_dependencies(file_path, content, language),
            "function_calls": find_function_calls_by_language(content, language),
            "language": language
        }
        
        print(f"  Found {len(file_info['imports'])} imports and {len(file_info['function_calls'])} function calls")
        return file_info
    
    except Exception as e:
        print(f"  Error analyzing {file_path}: {str(e)}")
        return {
            "path": file_path,
            "imports": [],
            "function_calls": [],
            "language": "unknown",
            "error": str(e)
        }

def build_dependency_graph(file_analyses):
    """
    Build a dependency graph based on the file analyses
    """
    graph = {
        "nodes": [],
        "edges": []
    }
    
    # Track node IDs to avoid duplicates
    node_ids = set()
    
    # First, add all files as nodes
    for file_info in file_analyses:
        file_path = file_info["path"]
        if file_path not in node_ids:
            node_ids.add(file_path)
            graph["nodes"].append({
                "id": file_path,
                "type": "file",
                "label": os.path.basename(file_path)
            })
    
    # Then add edges based on imports
    for file_info in file_analyses:
        source_file = file_info["path"]
        
        # Process imports
        for import_info in file_info["imports"]:
            if import_info["type"] == "import":
                module = import_info["module"]
                
                # Try to match the module to a file in our analysis
                for target_file_info in file_analyses:
                    target_file = target_file_info["path"]
                    # Simple heuristic: check if the file name matches the module name
                    if module in target_file or module.replace('.', '/') in target_file:
                        graph["edges"].append({
                            "source": source_file,
                            "target": target_file,
                            "type": "import"
                        })
            elif import_info["type"] == "from_import":
                module = import_info["module"]
                
                # Similar logic as above
                for target_file_info in file_analyses:
                    target_file = target_file_info["path"]
                    if module in target_file or module.replace('.', '/') in target_file:
                        graph["edges"].append({
                            "source": source_file,
                            "target": target_file,
                            "type": "from_import"
                        })
    
    return graph

def export_as_dot(graph, output_file):
    """
    Export the graph in DOT format (for Graphviz)
    """
    with open(output_file, 'w') as f:
        f.write('digraph DependencyGraph {\n')
        f.write('  node [shape=box];\n')
        
        # Write nodes
        for node in graph["nodes"]:
            node_id = node["id"].replace('/', '_').replace('.', '_').replace('-', '_')
            f.write(f'  {node_id} [label="{node["label"]}"];\n')
        
        # Write edges
        for edge in graph["edges"]:
            source = edge["source"].replace('/', '_').replace('.', '_').replace('-', '_')
            target = edge["target"].replace('/', '_').replace('.', '_').replace('-', '_')
            f.write(f'  {source} -> {target} [label="{edge["type"]}"];\n')
        
        f.write('}\n')
    
    print(f"DOT file exported to {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python dependency_graph.py <folder_path> [options]")
        print("Options:")
        print("  --output-format=<formats>  Comma-separated list of output formats (dot,json)")
        print("  --output-dir=<dir>        Custom output directory (default: 'outputs')")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    # Default options
    output_formats = ["json"]
    output_dir = "outputs"
    
    # Parse additional options
    for arg in sys.argv[2:]:
        if arg.startswith('--output-format='):
            formats = arg[16:].split(',')
            output_formats = [fmt.strip() for fmt in formats]
        elif arg.startswith('--output-dir='):
            output_dir = arg[13:]
    
    if not os.path.exists(folder_path):
        print(f"Error: The path '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Walk through the directory and analyze Python files
    file_analyses = []
    supported_files = []
    
    print("Finding files to analyze...")
    for root, dirs, files in os.walk(folder_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if (ext == '.py' or 
                ext in ['.js', '.jsx', '.ts', '.tsx'] or 
                ext in ['.cpp', '.cc', '.hpp', '.h']) and not file.startswith('.'):
                full_path = os.path.join(root, file)
                supported_files.append(full_path)
    
    print(f"Found {len(supported_files)} files to analyze")
    
    # Analyze each file
    print("\nAnalyzing files for dependencies...")
    for file_path in supported_files:
        language = detect_language(file_path)
        file_info = analyze_file(file_path, language)
        file_analyses.append(file_info)
        
    # Build the dependency graph
    print("\nBuilding dependency graph...")
    graph = build_dependency_graph(file_analyses)
    print(f"Created graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
    
    # Get the folder name for the output file
    folder_name = os.path.basename(os.path.normpath(folder_path))
    
    # Export in requested formats
    for fmt in output_formats:
        if fmt.lower() == 'json':
            output_file = os.path.join(output_dir, f"{folder_name}_dependencies.json")
            with open(output_file, 'w') as f:
                json.dump(graph, f, indent=2)
            print(f"JSON dependency graph exported to {output_file}")
        
        elif fmt.lower() == 'dot':
            output_file = os.path.join(output_dir, f"{folder_name}_dependencies.dot")
            export_as_dot(graph, output_file)
            print("To visualize the DOT file, use Graphviz: dot -Tpng -o dependencies.png " + output_file)
    
    print("\nDependency analysis complete!")

if __name__ == "__main__":
    main()
