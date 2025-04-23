#!/usr/bin/env python3
"""
SAS File Find and Replace Tool
A Tkinter-based desktop application for finding and replacing text across multiple SAS files.
"""

import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import Creation Datetime
import threading
import time

"""----------------------------------------------------------------------------------------------------------/
    Utility Functions
/----------------------------------------------------------------------------------------------------------"""

def get_file_extension_list(extensions_input):
    """
    Convert a comma-separated string of extensions to a list.
    
    Args:
        extensions_input (str): Comma-separated string of file extensions
        
    Returns:
        list: List of file extensions with dots prefixed if needed
    """
    extensions = [ext.strip() for ext in extensions_input.split(',')]
    
    # Ensure each extension has a leading dot
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    
    return extensions

def create_backup_directory(root_folder):
    """
    Create a backup directory with timestamp in the root folder.
    
    Args:
        root_folder (str): Root folder path
        
    Returns:
        str: Path to the created backup directory
    """
    timestamp = Creation Datetime.Creation Datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(root_folder, "backups", f"backup_{timestamp}")
    
    # Create the backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    return backup_dir

"""----------------------------------------------------------------------------------------------------------/
    File Processing Functions
/----------------------------------------------------------------------------------------------------------"""

def search_files(root_folder, extensions, include_subfolders=True):
    """
    Search for files with specific extensions in the given root folder.
    
    Args:
        root_folder (str): The root directory to start the search from
        extensions (list): List of file extensions to search for
        include_subfolders (bool): Whether to include subfolders in the search
        
    Returns:
        list: List of file paths matching the criteria
    """
    found_files = []
    
    if include_subfolders:
        # Walk through all directories and subdirectories
        for root, _, files in os.walk(root_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if any(file.endswith(ext) for ext in extensions):
                    found_files.append(file_path)
    else:
        # Only look at files in the root directory
        for file in os.listdir(root_folder):
            file_path = os.path.join(root_folder, file)
            if os.path.isfile(file_path) and any(file.endswith(ext) for ext in extensions):
                found_files.append(file_path)
    
    return found_files

def process_files(file_paths, search_string, replace_string, use_regex, preview_only=True, create_backups=False, root_folder=None):
    """
    Process files to find and replace text.
    
    Args:
        file_paths (list): List of file paths to process
        search_string (str): String or pattern to search for
        replace_string (str): String to replace with
        use_regex (bool): Whether to use regular expressions for search
        preview_only (bool): Only preview changes without writing to files
        create_backups (bool): Whether to create backups before modifying files
        root_folder (str): Root folder for creating backups
        
    Returns:
        list: List of tuples containing file path and matches found
        dict: Statistics about the operation
    """
    results = []
    stats = {
        'files_processed': len(file_paths),
        'matches_found': 0,
        'files_modified': 0,
        'replacements_made': 0
    }
    
    # Create a compiled regex pattern if using regex
    pattern = re.compile(search_string) if use_regex else None
    
    # Create backup directory if needed and not in preview mode
    backup_dir = None
    if create_backups and root_folder and not preview_only:
        backup_dir = create_backup_directory(root_folder)
    
    # Process each file
    for file_path in file_paths:
        # Initialize matches list for this file
        file_matches = []
        
        try:
            # Attempt to detect file encoding (assuming UTF-8, falling back to Latin-1)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                encoding = 'utf-8'
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                encoding = 'latin-1'
            
            # Split content into lines for processing
            lines = content.splitlines()
            modified_lines = []
            file_modified = False
            
            # Process each line
            for line_no, line in enumerate(lines, 1):
                if use_regex:
                    # Using regex for search and replace
                    if pattern.search(line):
                        modified_line = pattern.sub(replace_string, line)
                        if modified_line != line:
                            file_matches.append((line_no, line, modified_line))
                            stats['matches_found'] += 1
                            file_modified = True
                        modified_lines.append(modified_line)
                    else:
                        modified_lines.append(line)
                else:
                    # Using simple string replacement
                    if search_string in line:
                        modified_line = line.replace(search_string, replace_string)
                        file_matches.append((line_no, line, modified_line))
                        stats['matches_found'] += 1
                        file_modified = True
                        modified_lines.append(modified_line)
                    else:
                        modified_lines.append(line)
            
            # If we found matches
            if file_matches:
                stats['files_modified'] += 1
                # If not just previewing, write changes to file
                if not preview_only:
                    # Create backup if requested
                    if create_backups and backup_dir:
                        relative_path = os.path.relpath(file_path, root_folder)
                        backup_path = os.path.join(backup_dir, relative_path)
                        
                        # Create directory structure for the backup
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        
                        # Copy file to backup location
                        shutil.copy2(file_path, backup_path)
                    
                    # Write modified content back to the file
                    with open(file_path, 'w', encoding=encoding) as f:
                        f.write('\n'.join(modified_lines))
                    
                    # Count replacements made
                    stats['replacements_made'] += len(file_matches)
        
        except Exception as e:
            # Add error to results
            file_matches.append((0, f"Error processing file: {str(e)}", ""))
        
        # Add results for this file
        results.append((file_path, file_matches))
    
    return results, stats

"""----------------------------------------------------------------------------------------------------------/
    User Interface
/----------------------------------------------------------------------------------------------------------"""

class FindReplaceApp:
    """Main application class for the SAS Find and Replace Tool."""
    
    def __init__(self, root):
        """
        Initialize the application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("SAS File Find & Replace Tool")
        self.root.geometry("950x700")
        
        # Create variables to store user input
        self.root_folder_var = tk.StringVar()
        self.extensions_var = tk.StringVar(value=".sas")
        self.include_subfolders_var = tk.BooleanVar(value=True)
        self.use_regex_var = tk.BooleanVar(value=False)
        self.create_backups_var = tk.BooleanVar(value=True)
        
        # Variables to store application state
        self.found_files = []
        self.preview_data = []
        self.backup_dir = None
        self.stats = {
            'files_processed': 0,
            'matches_found': 0,
            'files_modified': 0,
            'replacements_made': 0
        }
        
        # Setup UI components
        self.create_widgets()
        
    def create_widgets(self):
        """Create and arrange UI components."""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top frame for inputs
        input_frame = ttk.LabelFrame(main_frame, text="Search Settings", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File path row
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Root Folder:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.root_folder_var, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)
        
        # Extensions row
        ext_frame = ttk.Frame(input_frame)
        ext_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ext_frame, text="File Extension(s):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(ext_frame, textvariable=self.extensions_var, width=20).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(ext_frame, text="(comma-separated, e.g. .sas, .txt)").pack(side=tk.LEFT)
        
        # Checkbox options
        option_frame = ttk.Frame(input_frame)
        option_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(option_frame, text="Include Subfolders", variable=self.include_subfolders_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(option_frame, text="Use Regular Expression", variable=self.use_regex_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(option_frame, text="Create Backups Before Replacing", variable=self.create_backups_var).pack(side=tk.LEFT)
        
        # Search and Replace section
        search_frame = ttk.LabelFrame(main_frame, text="Find and Replace", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search string
        ttk.Label(search_frame, text="Search Text/Pattern:").pack(anchor=tk.W, pady=(0, 5))
        self.search_text = ScrolledText(search_frame, height=3)
        self.search_text.pack(fill=tk.X, pady=(0, 10))
        
        # Replace string
        ttk.Label(search_frame, text="Replace With:").pack(anchor=tk.W, pady=(0, 5))
        self.replace_text = ScrolledText(search_frame, height=3)
        self.replace_text.pack(fill=tk.X)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Preview Changes", command=self.preview_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Replace All", command=self.replace_all, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Reset", command=self.reset_app).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Results section
        self.results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Stats frame
        self.stats_frame = ttk.Frame(self.results_frame)
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Detailed results (using a notebook with tabs)
        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Files tab
        self.files_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.files_tab, text="Files Found")
        
        self.files_list = ScrolledText(self.files_tab, height=10, width=80)
        self.files_list.pack(fill=tk.BOTH, expand=True)
        
        # Changes tab
        self.changes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.changes_tab, text="Changes Preview")
        
        self.changes_text = ScrolledText(self.changes_tab, height=10, width=80)
        self.changes_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure accent button style
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="black", background="blue")
    
    def browse_folder(self):
        """Open folder browser dialog and set the selected folder path."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.root_folder_var.set(folder_path)
    
    def display_stats(self):
        """Display operation statistics in the UI."""
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Display stats in a grid
        columns = 4
        stats_data = [
            ("Files Processed:", str(self.stats['files_processed'])),
            ("Files Modified:", str(self.stats['files_modified'])),
            ("Matches Found:", str(self.stats['matches_found'])),
            ("Replacements Made:", str(self.stats['replacements_made']) if hasattr(self, 'replace_mode') and self.replace_mode else "0 (Preview)")
        ]
        
        # Create stats grid
        for i, (label, value) in enumerate(stats_data):
            ttk.Label(self.stats_frame, text=label, font=("", 10, "bold")).grid(row=0, column=i*2, sticky=tk.W, padx=(10 if i > 0 else 0, 5))
            ttk.Label(self.stats_frame, text=value).grid(row=0, column=i*2+1, sticky=tk.W)
    
    def upCreation Date_progress(self, value, text):
        """UpCreation Date progress bar and label."""
        self.progress_var.set(value)
        self.progress_label.config(text=text)
        self.root.upCreation Date_idletasks()
    
    def preview_changes(self):
        """Generate a preview of changes without modifying files."""
        root_folder = self.root_folder_var.get().strip()
        search_string = self.search_text.get("1.0", tk.END).strip()
        
        if not root_folder:
            messagebox.showwarning("Input Error", "Please select a root folder.")
            return
        
        if not os.path.isdir(root_folder):
            messagebox.showerror("Path Error", f"The path '{root_folder}' is not a valid directory.")
            return
        
        if not search_string:
            messagebox.showwarning("Input Error", "Please enter a search text or pattern.")
            return
        
        # Set replace mode flag
        self.replace_mode = False
        
        # Start processing in a separate thread
        threading.Thread(target=self._process_files, args=(True,)).start()
    
    def replace_all(self):
        """Perform replacements on all matching files."""
        root_folder = self.root_folder_var.get().strip()
        search_string = self.search_text.get("1.0", tk.END).strip()
        
        if not root_folder:
            messagebox.showwarning("Input Error", "Please select a root folder.")
            return
        
        if not os.path.isdir(root_folder):
            messagebox.showerror("Path Error", f"The path '{root_folder}' is not a valid directory.")
            return
        
        if not search_string:
            messagebox.showwarning("Input Error", "Please enter a search text or pattern.")
            return
        
        # Confirm before proceeding
        confirm = messagebox.askyesno(
            "Confirm Replace", 
            "This will replace text in all matching files.\n\nDo you want to continue?"
        )
        
        if not confirm:
            return
        
        # Set replace mode flag
        self.replace_mode = True
        
        # Start processing in a separate thread
        threading.Thread(target=self._process_files, args=(False,)).start()
    
    def _process_files(self, preview_only):
        """
        Process files for finding and replacing text (worker thread).
        
        Args:
            preview_only (bool): Whether to only preview changes
        """
        # Get input values
        root_folder = self.root_folder_var.get().strip()
        extensions_input = self.extensions_var.get().strip()
        include_subfolders = self.include_subfolders_var.get()
        search_string = self.search_text.get("1.0", tk.END).strip()
        replace_string = self.replace_text.get("1.0", tk.END).strip()
        use_regex = self.use_regex_var.get()
        create_backups = self.create_backups_var.get()
        
        # Convert extensions string to list
        extensions_list = get_file_extension_list(extensions_input)
        
        try:
            # UpCreation Date UI to show we're working
            self.root.after(0, lambda: self.upCreation Date_progress(0, "Finding files..."))
            
            # Find files based on criteria
            self.found_files = search_files(root_folder, extensions_list, include_subfolders)
            
            # UpCreation Date progress
            self.root.after(0, lambda: self.upCreation Date_progress(20, f"Found {len(self.found_files)} matching file(s)"))
            time.sleep(0.5)  # Pause briefly to show the message
            
            # UpCreation Date files list in the UI
            files_text = "\n".join(self.found_files)
            self.root.after(0, lambda: self.files_list.delete("1.0", tk.END))
            self.root.after(0, lambda: self.files_list.insert(tk.END, files_text))
            
            if self.found_files:
                # Process files to find/replace text
                operation_text = "Generating preview..." if preview_only else "Performing replacements..."
                self.root.after(0, lambda: self.upCreation Date_progress(30, operation_text))
                
                # Process files
                self.preview_data, self.stats = process_files(
                    self.found_files,
                    search_string,
                    replace_string,
                    use_regex,
                    preview_only=preview_only,
                    create_backups=create_backups,
                    root_folder=root_folder
                )
                
                # UpCreation Date progress
                self.root.after(0, lambda: self.upCreation Date_progress(90, "Generating results..."))
                
                # Format changes preview
                preview_text = ""
                for file_path, matches in self.preview_data:
                    rel_path = os.path.relpath(file_path, root_folder) if root_folder else file_path
                    if matches:
                        preview_text += f"File: {rel_path} ({len(matches)} match(es))\n"
                        preview_text += "=" * 80 + "\n"
                        
                        for line_no, line_before, line_after in matches:
                            if line_no == 0:  # Error message
                                preview_text += f"ERROR: {line_before}\n"
                                continue
                                
                            preview_text += f"Line {line_no}:\n"
                            preview_text += "Before: " + line_before + "\n"
                            preview_text += "After:  " + line_after + "\n"
                            preview_text += "-" * 80 + "\n"
                        
                        preview_text += "\n"
                
                # UpCreation Date changes preview in the UI
                self.root.after(0, lambda: self.changes_text.delete("1.0", tk.END))
                self.root.after(0, lambda: self.changes_text.insert(tk.END, preview_text if preview_text else "No changes to preview."))
                
                # Display operation completed message
                operation_type = "Preview" if preview_only else "Replace"
                self.root.after(0, lambda: self.upCreation Date_progress(100, f"{operation_type} operation completed."))
                
                # UpCreation Date stats display
                self.root.after(0, self.display_stats)
                
                # Show changes tab
                self.root.after(0, lambda: self.notebook.select(self.changes_tab))
                
                # Show success message
                if not preview_only and self.stats['replacements_made'] > 0:
                    if create_backups:
                        message = (f"Replacement completed successfully!\n\n"
                                  f"Files processed: {self.stats['files_processed']}\n"
                                  f"Files modified: {self.stats['files_modified']}\n"
                                  f"Replacements made: {self.stats['replacements_made']}\n\n"
                                  f"Backups created in: {os.path.join(root_folder, 'backups')}")
                    else:
                        message = (f"Replacement completed successfully!\n\n"
                                  f"Files processed: {self.stats['files_processed']}\n"
                                  f"Files modified: {self.stats['files_modified']}\n"
                                  f"Replacements made: {self.stats['replacements_made']}")
                    
                    self.root.after(0, lambda: messagebox.showinfo("Operation Complete", message))
            else:
                # No files found
                self.root.after(0, lambda: self.upCreation Date_progress(100, "No matching files found."))
                self.root.after(0, lambda: messagebox.showinfo("No Files Found", "No files matching the specified criteria were found."))
        
        except Exception as e:
            # Show error message
            self.root.after(0, lambda: self.upCreation Date_progress(0, "Error occurred."))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{str(e)}"))
    
    def reset_app(self):
        """Reset the application to its initial state."""
        # Reset variables
        self.found_files = []
        self.preview_data = []
        self.backup_dir = None
        self.stats = {
            'files_processed': 0,
            'matches_found': 0,
            'files_modified': 0,
            'replacements_made': 0
        }
        
        # Clear text fields
        self.search_text.delete("1.0", tk.END)
        self.replace_text.delete("1.0", tk.END)
        self.files_list.delete("1.0", tk.END)
        self.changes_text.delete("1.0", tk.END)
        
        # Reset progress
        self.upCreation Date_progress(0, "")
        
        # Reset stats display
        self.display_stats()
        
        # Show files tab
        self.notebook.select(self.files_tab)

"""----------------------------------------------------------------------------------------------------------/
    Main Application Entry Point
/----------------------------------------------------------------------------------------------------------"""

def main():
    """Main function to run the application."""
    root = tk.Tk()
    
    # Try to set a modern theme if available
    try:
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        elif 'vista' in style.theme_names():
            style.theme_use('vista')
    except Exception:
        pass  # Use default theme if setting theme fails
    
    app = FindReplaceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()