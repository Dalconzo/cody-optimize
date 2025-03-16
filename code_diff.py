#!/usr/bin/env python3
import os
import sys
import json
import re
import argparse
import tempfile
import subprocess
from collections import defaultdict

def clone_github_repo(repo_url, target_dir=None, branch=None, commit=None):
    """
    Clone a GitHub repository at a specific branch or commit
    """
    if target_dir is None:
        target_dir = tempfile.mkdtemp()
    
    print(f"Cloning {repo_url} to {target_dir}...")
    
    # Basic clone command
    clone_cmd = ["git", "clone", repo_url, target_dir]
    if branch:
        clone_cmd.extend(["--branch", branch, "--single-branch"])
    
    try:
        subprocess.run(clone_cmd, check=True, capture_output=True)
        
        # If a specific commit is requested, checkout that commit
        if commit:
            subprocess.run(["git", "checkout", commit], cwd=target_dir, check=True, capture_output=True)
            
        # Get the current commit hash
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=target_dir, check=True, capture_output=True, text=True)
        current_commit = result.stdout.strip()
        
        print(f"Repository cloned successfully at commit {current_commit}")
        return target_dir, current_commit
    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
        print(f"Output: {e.stdout.decode('utf-8')}")
        print(f"Error: {e.stderr.decode('utf-8')}")
        raise

def get_file_content(file_path):
    """
    Safely read and return file content
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def extract_functions_and_classes(content, language):
    """
    Extract functions and classes from code content based on language
    """
    # Dictionary to store extracted items with their full definitions
    extracted = {
        "functions": {},
        "classes": {},
        "methods": {}
    }
    
    if not content:
        return extracted
    
    if language == "python":
        # Extract Python functions with their full definitions
        function_pattern = re.compile(r'^(\s*)def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?\s*:(.*?)(?=^\1\S|\Z)', re.MULTILINE | re.DOTALL)
        for match in function_pattern.finditer(content):
            indentation = match.group(1)
            name = match.group(2)
            params = match.group(3)
            return_type = match.group(4)
            body = match.group(5)
            
            # If indentation is non-empty, it's a method, otherwise a function
            if indentation:
                extracted["methods"][name] = {
                    "params": params.strip(),
                    "return_type": return_type.strip() if return_type else None,
                    "body": body.strip()
                }
            else:
                extracted["functions"][name] = {
                    "params": params.strip(),
                    "return_type": return_type.strip() if return_type else None,
                    "body": body.strip()
                }
        
        # Extract Python classes with their full definitions
        class_pattern = re.compile(r'^class\s+([a-zA-Z0-9_]+)(?:\(([^)]*)\))?\s*:(.*?)(?=^class|\Z)', re.MULTILINE | re.DOTALL)
        for match in class_pattern.finditer(content):
            name = match.group(1)
            inheritance = match.group(2)
            body = match.group(3)
            
            extracted["classes"][name] = {
                "inheritance": inheritance.strip() if inheritance else None,
                "body": body.strip()
            }
            
    elif language in ["javascript", "typescript"]:
        # Extract JavaScript/TypeScript functions
        function_pattern = re.compile(r'function\s+([a-zA-Z0-9_$]+)\s*\(([^)]*)\)\s*{(.*?)(?=^function|\Z)', re.MULTILINE | re.DOTALL)
        for match in function_pattern.finditer(content):
            name = match.group(1)
            params = match.group(2)
            body = match.group(3)
            
            extracted["functions"][name] = {
                "params": params.strip(),
                "body": body.strip()
            }
        
        # Extract arrow functions assigned to variables
        arrow_pattern = re.compile(r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>\s*{(.*?)}', re.MULTILINE | re.DOTALL)
        for match in arrow_pattern.finditer(content):
            name = match.group(1)
            params = match.group(2)
            body = match.group(3)
            
            extracted["functions"][name] = {
                "params": params.strip(),
                "body": body.strip(),
                "type": "arrow"
            }
        
        # Extract classes and their methods
        class_pattern = re.compile(r'class\s+([a-zA-Z0-9_$]+)(?:\s+extends\s+([a-zA-Z0-9_$]+))?\s*{(.*?)}', re.MULTILINE | re.DOTALL)
        for match in class_pattern.finditer(content):
            name = match.group(1)
            inheritance = match.group(2)
            body = match.group(3)
            
            extracted["classes"][name] = {
                "inheritance": inheritance,
                "body": body.strip()
            }
            
            # Extract methods from class body
            method_pattern = re.compile(r'(?:async\s+)?([a-zA-Z0-9_$]+)\s*\(([^)]*)\)\s*{(.*?)}', re.MULTILINE | re.DOTALL)
            for method_match in method_pattern.finditer(body):
                method_name = method_match.group(1)
                method_params = method_match.group(2)
                method_body = method_match.group(3)
                
                # Skip constructor if looking at JavaScript
                if method_name != "constructor":
                    extracted["methods"][f"{name}.{method_name}"] = {
                        "params": method_params.strip(),
                        "body": method_body.strip()
                    }
    
    elif language in ["cpp", "c"]:
        # Extract C/C++ functions (simplified)
        function_pattern = re.compile(r'([a-zA-Z0-9_:]+(?:\s*<[^>]*>)?)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*(?:const)?\s*{(.*?)(?=^[a-zA-Z0-9_:]+(?:\s*<[^>]*>)?\s+[a-zA-Z0-9_]+\s*\(|\Z)', re.MULTILINE | re.DOTALL)
        for match in function_pattern.finditer(content):
            return_type = match.group(1)
            name = match.group(2)
            params = match.group(3)
            body = match.group(4)
            
            extracted["functions"][name] = {
                "return_type": return_type.strip(),
                "params": params.strip(),
                "body": body.strip()
            }
        
        # Extract C++ classes
        class_pattern = re.compile(r'class\s+([a-zA-Z0-9_]+)(?:\s*:\s*(?:public|private|protected)\s+([a-zA-Z0-9_]+))?\s*{(.*?)};', re.MULTILINE | re.DOTALL)
        for match in class_pattern.finditer(content):
            name = match.group(1)
            inheritance = match.group(2)
            body = match.group(3)
            
            extracted["classes"][name] = {
                "inheritance": inheritance.strip() if inheritance else None,
                "body": body.strip()
            }
    
    return extracted

def detect_language(file_path):
    """
    Detect the programming language from file extension
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.py':
        return "python"
    elif ext in ['.js', '.jsx']:
        return "javascript"
    elif ext in ['.ts', '.tsx']:
        return "typescript"
    elif ext in ['.c', '.h']:
        return "c"
    elif ext in ['.cpp', '.cc', '.hpp']:
        return "cpp"
    elif ext in ['.java']:
        return "java"
    # Add more languages as needed
    return "unknown"

def analyze_codebase_structure(repo_path):
    """
    Analyze the structure of a codebase, extracting functions, classes, and methods
    """
    code_structure = {}
    file_count = 0
    
    print(f"Analyzing codebase structure in {repo_path}...")
    
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories and common non-source directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
        
        for file in files:
            # Skip hidden files and non-source files
            if file.startswith('.') or file.endswith(('.md', '.txt', '.json', '.xml', '.csv')):
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            language = detect_language(file_path)
            if language == "unknown":
                continue
                
            content = get_file_content(file_path)
            if content:
                extracted = extract_functions_and_classes(content, language)
                
                # Only add files that have functions, classes, or methods
                if (extracted["functions"] or extracted["classes"] or extracted["methods"]):
                    code_structure[rel_path] = {
                        "language": language,
                        "functions": extracted["functions"],
                        "classes": extracted["classes"],
                        "methods": extracted["methods"]
                    }
                    file_count += 1
    
    print(f"Analyzed {file_count} source files")
    return code_structure

def compare_structures(old_structure, new_structure):
    """
    Compare two code structures and identify semantic changes
    """
    changes = {
        "added_files": [],
        "removed_files": [],
        "modified_files": [],
        "function_changes": {
            "added": [],
            "removed": [],
            "modified": []
        },
        "class_changes": {
            "added": [],
            "removed": [],
            "modified": []
        },
        "method_changes": {
            "added": [],
            "removed": [],
            "modified": []
        }
    }
    
    # Find added and removed files
    old_files = set(old_structure.keys())
    new_files = set(new_structure.keys())
    
    changes["added_files"] = list(new_files - old_files)
    changes["removed_files"] = list(old_files - new_files)
    
    # Find modified files and analyze changes within them
    common_files = old_files.intersection(new_files)
    
    for file in common_files:
        old_file = old_structure[file]
        new_file = new_structure[file]
        
        file_changes = {
            "functions": {"added": [], "removed": [], "modified": []},
            "classes": {"added": [], "removed": [], "modified": []},
            "methods": {"added": [], "removed": [], "modified": []}
        }
        
        # Compare functions
        old_functions = set(old_file["functions"].keys())
        new_functions = set(new_file["functions"].keys())
        
        for func in new_functions - old_functions:
            file_changes["functions"]["added"].append({
                "name": func,
                "details": new_file["functions"][func]
            })
            changes["function_changes"]["added"].append({
                "file": file,
                "name": func
            })
        
        for func in old_functions - new_functions:
            file_changes["functions"]["removed"].append({
                "name": func,
                "details": old_file["functions"][func]
            })
            changes["function_changes"]["removed"].append({
                "file": file,
                "name": func
            })
        
        # For functions that exist in both, compare their bodies
        for func in old_functions.intersection(new_functions):
            old_func = old_file["functions"][func]
            new_func = new_file["functions"][func]
            
            # Simple approach: check if the body has changed
            # In a real implementation, you'd want more sophisticated comparison
            if old_func["body"] != new_func["body"] or old_func.get("params") != new_func.get("params"):
                file_changes["functions"]["modified"].append({
                    "name": func,
                    "old": old_func,
                    "new": new_func
                })
                changes["function_changes"]["modified"].append({
                    "file": file,
                    "name": func
                })
        
        # Similarly compare classes and methods
        old_classes = set(old_file["classes"].keys())
        new_classes = set(new_file["classes"].keys())
        
        for cls in new_classes - old_classes:
            file_changes["classes"]["added"].append({
                "name": cls,
                "details": new_file["classes"][cls]
            })
            changes["class_changes"]["added"].append({
                "file": file,
                "name": cls
            })
        
        for cls in old_classes - new_classes:
            file_changes["classes"]["removed"].append({
                "name": cls,
                "details": old_file["classes"][cls]
            })
            changes["class_changes"]["removed"].append({
                "file": file,
                "name": cls
            })
        
                # Continue comparing classes that exist in both versions
        for cls in old_classes.intersection(new_classes):
            old_cls = old_file["classes"][cls]
            new_cls = new_file["classes"][cls]
            
            # Check for changes in class body or inheritance
            if old_cls["body"] != new_cls["body"] or old_cls.get("inheritance") != new_cls.get("inheritance"):
                file_changes["classes"]["modified"].append({
                    "name": cls,
                    "old": old_cls,
                    "new": new_cls
                })
                changes["class_changes"]["modified"].append({
                    "file": file,
                    "name": cls
                })
        
        # Compare methods
        old_methods = set(old_file["methods"].keys())
        new_methods = set(new_file["methods"].keys())
        
        for method in new_methods - old_methods:
            file_changes["methods"]["added"].append({
                "name": method,
                "details": new_file["methods"][method]
            })
            changes["method_changes"]["added"].append({
                "file": file,
                "name": method
            })
        
        for method in old_methods - new_methods:
            file_changes["methods"]["removed"].append({
                "name": method,
                "details": old_file["methods"][method]
            })
            changes["method_changes"]["removed"].append({
                "file": file,
                "name": method
            })
        
        for method in old_methods.intersection(new_methods):
            old_method = old_file["methods"][method]
            new_method = new_file["methods"][method]
            
            if old_method["body"] != new_method["body"] or old_method.get("params") != new_method.get("params"):
                file_changes["methods"]["modified"].append({
                    "name": method,
                    "old": old_method,
                    "new": new_method
                })
                changes["method_changes"]["modified"].append({
                    "file": file,
                    "name": method
                })
        
        # If any changes were detected in this file, add it to modified files
        if (file_changes["functions"]["added"] or file_changes["functions"]["removed"] or file_changes["functions"]["modified"] or
            file_changes["classes"]["added"] or file_changes["classes"]["removed"] or file_changes["classes"]["modified"] or
            file_changes["methods"]["added"] or file_changes["methods"]["removed"] or file_changes["methods"]["modified"]):
            changes["modified_files"].append({
                "file": file,
                "changes": file_changes
            })
    
    return changes

def categorize_semantic_changes(changes):
    """
    Group changes by semantic meaning rather than just by file
    """
    semantic_groups = {
        "api_changes": [],
        "feature_additions": [],
        "refactorings": [],
        "bug_fixes": [],
        "performance_improvements": [],
        "other_changes": []
    }
    
    # Analyze commit messages and code patterns to categorize changes
    # This is a simplified implementation - a real one would use more sophisticated heuristics
    
    # Example heuristic: Functions with "fix" in the name might be bug fixes
    for func in changes["function_changes"]["added"] + changes["function_changes"]["modified"]:
        func_name = func["name"].lower()
        if "fix" in func_name or "bug" in func_name:
            semantic_groups["bug_fixes"].append(func)
        elif "perf" in func_name or "optimize" in func_name or "performance" in func_name:
            semantic_groups["performance_improvements"].append(func)
        elif "api" in func_name or func_name.startswith("get") or func_name.startswith("set"):
            semantic_groups["api_changes"].append(func)
        elif "feature" in func_name or "add" in func_name:
            semantic_groups["feature_additions"].append(func)
        elif "refactor" in func_name:
            semantic_groups["refactorings"].append(func)
        else:
            semantic_groups["other_changes"].append(func)
    
    # Similar logic could be applied to classes and methods
    
    return semantic_groups

def generate_change_report(changes, semantic_groups, old_commit, new_commit, output_format="json"):
    """
    Generate a structured report of the changes
    """
    report = {
        "metadata": {
            "old_commit": old_commit,
            "new_commit": new_commit,
            "comparison_date": datetime.datetime.now().isoformat()
        },
        "summary": {
            "added_files": len(changes["added_files"]),
            "removed_files": len(changes["removed_files"]),
            "modified_files": len(changes["modified_files"]),
            "added_functions": len(changes["function_changes"]["added"]),
            "removed_functions": len(changes["function_changes"]["removed"]),
            "modified_functions": len(changes["function_changes"]["modified"]),
            "added_classes": len(changes["class_changes"]["added"]),
            "removed_classes": len(changes["class_changes"]["removed"]),
            "modified_classes": len(changes["class_changes"]["modified"]),
            "added_methods": len(changes["method_changes"]["added"]),
            "removed_methods": len(changes["method_changes"]["removed"]),
            "modified_methods": len(changes["method_changes"]["modified"])
        },
        "semantic_grouping": semantic_groups,
        "detailed_changes": changes
    }
    
    if output_format == "json":
        return json.dumps(report, indent=2)
    else:
        # Could implement other formats like HTML, Markdown, etc.
        return json.dumps(report, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Analyze semantic code changes between two versions of a repository')
    parser.add_argument('repo_url', help='GitHub repository URL')
    parser.add_argument('--old', required=True, help='Old version (branch, tag, or commit hash)')
    parser.add_argument('--new', required=True, help='New version (branch, tag, or commit hash)')
    parser.add_argument('--output-dir', default='outputs', help='Output directory for results')
    parser.add_argument('--semantic-grouping', action='store_true', help='Group changes by semantic meaning')
    parser.add_argument('--format', choices=['json', 'html', 'md'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Clone the old version
    old_dir = tempfile.mkdtemp()
    old_dir, old_commit = clone_github_repo(args.repo_url, old_dir, commit=args.old)
    
    # Clone the new version
    new_dir = tempfile.mkdtemp()
    new_dir, new_commit = clone_github_repo(args.repo_url, new_dir, commit=args.new)
    
    # Analyze both codebases
    print("\nAnalyzing old codebase...")
    old_structure = analyze_codebase_structure(old_dir)
    
    print("\nAnalyzing new codebase...")
    new_structure = analyze_codebase_structure(new_dir)
    
    # Compare the structures
    print("\nComparing codebases...")
    changes = compare_structures(old_structure, new_structure)
    
    # Generate semantic grouping if requested
    semantic_groups = {}
    if args.semantic_grouping:
        print("Generating semantic grouping of changes...")
        semantic_groups = categorize_semantic_changes(changes)
    
    # Generate the report
    print("Generating change report...")
    report = generate_change_report(changes, semantic_groups, old_commit, new_commit, args.format)
    
    # Save the report
    repo_name = args.repo_url.split('/')[-1].replace('.git', '')
    output_file = os.path.join(args.output_dir, f"{repo_name}_changes_{old_commit[:7]}_{new_commit[:7]}.json")
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"\nChange analysis complete! Report saved to {output_file}")
    
    # Summary of findings
    print("\nSummary of changes:")
    print(f"  Added files: {len(changes['added_files'])}")
    print(f"  Removed files: {len(changes['removed_files'])}")
    print(f"  Modified files: {len(changes['modified_files'])}")
    print(f"  Added functions: {len(changes['function_changes']['added'])}")
    print(f"  Removed functions: {len(changes['function_changes']['removed'])}")
    print(f"  Modified functions: {len(changes['function_changes']['modified'])}")
    print(f"  Added classes: {len(changes['class_changes']['added'])}")
    print(f"  Removed classes: {len(changes['class_changes']['removed'])}")
    print(f"  Modified classes: {len(changes['class_changes']['modified'])}")
    
    # Cleanup temporary directories
    import shutil
    shutil.rmtree(old_dir)
    shutil.rmtree(new_dir)

if __name__ == "__main__":
    import datetime  # Import here for the timestamp in the report
    main()

