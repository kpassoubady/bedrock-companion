import os
import json
import glob

SOURCE_DIR = "/Users/kangs/code/github/bedrock/day1/demos"
TARGET_DIR = "/Users/kangs/code/github/bedrock/day1/demos/generated_notebooks"

def create_notebook(py_file_path, target_dir):
    basename = os.path.basename(py_file_path)
    if not basename.endswith('.py'):
        return
    demo_name = basename[:-3]
    
    with open(py_file_path, 'r') as f:
        content = f.read()

    # Extract docstring if present
    docstring = ""
    code_content = content
    if content.startswith('"""'):
        end_idx = content.find('"""', 3)
        if end_idx != -1:
            docstring = content[3:end_idx].strip()
            code_content = content[end_idx+3:].strip()
            
    # Parse docstring for title
    title = docstring.split('\n')[0] if docstring else f"Demo: {demo_name}"
            
    # Create the notebook structure
    cells = []
    
    # Markdown title cell
    md_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [f"# {title}\n\n", "This notebook is a follow-along demo."]
    }
    cells.append(md_cell)
    
    # If docstring is present, add it as a markdown cell
    if docstring:
        desc_lines = docstring.split('\n')[1:]
        if desc_lines:
            desc_md = "\n".join(desc_lines).strip()
            if desc_md:
                cells.append({
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [line + "\n" for line in desc_md.split('\n')]
                })

    # Add pip install cell
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Install required dependencies\n",
            "!pip install boto3 --quiet"
        ]
    })
    
    source_lines = [line + '\n' for line in code_content.split('\n')]
    if source_lines and source_lines[-1] == '\n':
        source_lines = source_lines[:-1]
    
    code_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines
    }
    cells.append(code_cell)

    notebook = {
        "cells": cells,
        "metadata": {
            "colab": {
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 0
    }
    
    demo_target_dir = os.path.join(TARGET_DIR, demo_name)
    os.makedirs(demo_target_dir, exist_ok=True)
    
    ipynb_path = os.path.join(demo_target_dir, f"{demo_name}.ipynb")
    with open(ipynb_path, 'w') as f:
        json.dump(notebook, f, indent=2)
        
    readme_path = os.path.join(demo_target_dir, "README.md")
    colab_url = f"https://colab.research.google.com/github/OWNER/REPO/blob/main/day1/demos/{demo_name}/{demo_name}.ipynb"
    readme_content = f"""# {title}

This is a follow-along demo for students. 

## Instructions

1. Open `{demo_name}.ipynb` in Google Colab or run it locally.
2. Run the cells to see the demonstration.

**Open in Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab_url})
"""
    with open(readme_path, 'w') as f:
        f.write(readme_content)
        
    print(f"Created {ipynb_path}")

def main():
    py_files = glob.glob(os.path.join(SOURCE_DIR, "*.py"))
    print(f"Found files: {py_files}")
    for py_file in py_files:
        create_notebook(py_file, TARGET_DIR)

if __name__ == "__main__":
    main()
