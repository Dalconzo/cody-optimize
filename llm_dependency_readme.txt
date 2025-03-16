Analysis Depth Configuration
Adding a parameter to control analysis depth would help with large codebases:

def main():
    # Add this to command options
    max_depth = 3  # Default
    
    for arg in sys.argv[2:]:
        if arg.startswith('--max-depth='):
            max_depth = int(arg[12:])

Copy

Apply

Filtering Capabilities
Allow users to focus on specific dependencies:

# Add to options
dependency_types = ['all']  # Default to all
for arg in sys.argv[2:]:
    if arg.startswith('--dependency-types='):
        dependency_types = arg[19:].split(',')

Copy

Apply

Module Resolution Strategy
The current heuristic for mapping module names to files needs enhancement:

def resolve_module_path(module_name, source_file, language):
    """More accurate module resolution based on language conventions"""
    if language == 'python':
        # Handle Python's dot notation
        module_parts = module_name.split('.')
        # Look for __init__.py files and package structures
        
    elif language == 'javascript':
        # Handle Node.js resolution algorithm
        # Check for package.json, node_modules, etc.
        
    elif language == 'cpp':
        # Handle include paths differently for system vs local includes
        # May need to parse build files (CMakeLists.txt, etc.)

Copy

Apply

Graph Enrichment
Adding metadata to nodes and edges would provide more context:

# Enhanced node creation
node = {
    "id": file_path,
    "type": "file",
    "label": os.path.basename(file_path),
    "language": language,
    "size": os.path.getsize(file_path),
    "functions": len(file_info.get("function_calls", [])),
    "dependencies": len(file_info.get("imports", []))
}

Copy

Apply

Performance Optimization
For large codebases, add incremental analysis:

# Check if previous analysis exists
cache_file = os.path.join(output_dir, f"{folder_name}_analysis_cache.json")
file_analyses = []

if os.path.exists(cache_file) and not args.force_reanalysis:
    print("Loading previous analysis...")
    with open(cache_file, 'r') as f:
        file_analyses = json.load(f)
    
    # Only analyze new or modified files
    for file_path in supported_files:
        if not any(fa["path"] == file_path and 
                  os.path.getmtime(file_path) <= fa.get("analyzed_at", 0) 
                  for fa in file_analyses):
            language = detect_language(file_path)
            file_info = analyze_file(file_path, language)
            file_info["analyzed_at"] = time.time()
            file_analyses.append(file_info)

Copy

Apply

Visualization Enhancement
Add options for interactive visualization:

def export_as_html(graph, output_file):
    """Create an interactive D3.js visualization"""
    # Generate HTML with embedded D3.js
    with open(output_file, 'w') as f:
        f.write(HTML_TEMPLATE.replace('__DATA__', json.dumps(graph)))

Copy

Apply

These enhancements would make the dependency graph analyzer more robust, particularly for complex multi-language projects where understanding cross-file and cross-language dependencies is crucial for LLMs to generate accurate and contextually appropriate code.