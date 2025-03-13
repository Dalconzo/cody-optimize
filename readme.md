Codebase Extraction Tools - README
This repository contains three Python scripts for extracting and mapping codebases. Each tool serves a different purpose for code analysis and documentation.

1. dir_to_json.py - Directory Structure Mapper
This tool captures the complete directory structure of a codebase, including file contents.

Usage:
python dir_to_json.py <folder_path> [ignore_folders]

Copy

Execute

Parameters:
<folder_path>: Directory to analyze
[ignore_folders]: Optional comma-separated list of folder names to ignore (e.g., "node_modules,dist,build")
Example:
python dir_to_json.py ./my_project node_modules,venv

Output:
Creates a JSON file in the outputs directory named <folder_name>_structure.txt containing the complete directory structure with file contents for all text files under 1MB.

2. file_extractor.py - Specific File Finder
This tool searches for specific filenames across a directory structure and extracts their contents with line numbers.

Usage:
python file_extractor.py <folder_path> <target_files> [options]

Parameters:
<folder_path>: Directory to search within
<target_files>: Comma-separated list of filenames to find (e.g., "README.md,package.json")
Options:
--ignore-folders=<folders>: Comma-separated list of folder names to ignore
--ignore-extension: Match filenames without considering extensions
--output-dir=<dir>: Custom output directory (default: 'outputs')
--prefix=<prefix>: Custom prefix for output filename (default: 'extracted_')
Example:
python file_extractor.py ./my_project package.json,README.md --ignore-folders=node_modules,build --output-dir=results

Output:
Creates a JSON file in the specified output directory containing the found files organized by their original directory structure, with content split into numbered lines.

3. function_extractor.py - Code Structure Analyzer
This tool extracts function and class definitions from source code files to create a code map.

Usage:
python function_extractor.py <folder_path> [ignore_folders]

Parameters:
<folder_path>: Directory to analyze
[ignore_folders]: Optional comma-separated list of folder names to ignore (e.g., "node_modules,dist")
Example:
python function_extractor.py ./src test,vendor

Output:
Creates a JSON file in the outputs directory named <folder_name>_definitions.json containing the directory structure with function and class definitions extracted from recognized source files.

Supported Languages:
Python (.py)
JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
Java (.java)
C# (.cs)
C/C++ (.c, .cpp, .cc, .h, .hpp)
Technical Requirements
Python 3.6 or higher
No additional dependencies required (uses standard library modules only)
Each script creates an outputs directory if it doesn't exist. The tools handle binary files, large files, and permission issues gracefully with appropriate error messages.