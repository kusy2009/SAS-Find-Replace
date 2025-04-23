# SAS File Find and Replace Tool

A Tkinter-based desktop application for finding and replacing text across multiple SAS files with preview functionality.

## Features

- Select a root folder to search in
- Specify file extensions to target (default: .sas)
- Choose whether to include subfolders in the search
- Enter search text or regular expression patterns
- Preview changes before applying them
- Create automatic backups before making changes
- View detailed statistics about the operation
- Review line-by-line changes with before/after comparison

## Requirements

- Python 3.10 or higher
- Required Python packages:
  - tkinter (included in standard Python installation)
  - re (included in standard Python installation)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd sas-file-find-replace
   ```

2. Open the project in VS Code or your preferred editor

3. No additional installations required as tkinter is included in standard Python

## Usage

1. Launch the application:
   ```bash
   python sas_find_replace.py
   ```

2. Use the "Browse..." button to select a root folder

3. Adjust search settings:
   - Modify file extensions if needed (comma-separated)
   - Toggle inclusion of subfolders
   - Enable/disable regular expression mode
   - Choose whether to create backups

4. Enter the search text or pattern and the replacement text

5. Click "Preview Changes" to see what would be changed without modifying files

6. Once satisfied with the preview, click "Replace All" to apply changes

7. Review the results and detailed change information

## UI Description

The application has a clean, functional UI with the following layout:

- Top section:
  - Search settings (root folder, file extensions, subfolder option)
  - Find and replace inputs (search text, replace text, regex option)
  - Action buttons (Preview Changes, Replace All, Reset)

- Middle section:
  - Progress bar showing operation status

- Bottom section (tabbed interface):
  - "Files Found" tab showing all matching files
  - "Changes Preview" tab showing detailed before/after comparisons
  - Statistics summary showing operation results

## Comments Style

This project uses the following comment style for module headers and function descriptions:

```python
"""----------------------------------------------------------------------------------------------------------/
    Module or section description
/----------------------------------------------------------------------------------------------------------"""
```

For function documentation, standard docstrings with Args and Returns sections are used:

```python
def function_name(param1, param2):
    """
    Function description.
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
        
    Returns:
        type: Description of return value
    """
```