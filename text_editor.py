#!/usr/bin/env python3
"""
Simple Text Editor for JARVIS
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path

class TextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS Text Editor")
        self.root.geometry("800x600")
        
        self.current_file = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the text editor UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        edit_menu.add_command(label="Find", command=self.find_text)
        edit_menu.add_command(label="Replace", command=self.replace_text)
        
        # Text area
        self.text_area = tk.Text(self.root, wrap=tk.WORD, undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.text_area)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_area.yview)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def new_file(self):
        """Create a new file"""
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("JARVIS Text Editor - New File")
        self.status_bar.config(text="New file created")
        
    def open_file(self):
        """Open an existing file"""
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    
                self.current_file = file_path
                self.root.title(f"JARVIS Text Editor - {Path(file_path).name}")
                self.status_bar.config(text=f"Opened: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
                
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w') as file:
                    file.write(content)
                self.status_bar.config(text=f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """Save the file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w') as file:
                    file.write(content)
                    
                self.current_file = file_path
                self.root.title(f"JARVIS Text Editor - {Path(file_path).name}")
                self.status_bar.config(text=f"Saved as: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                
    def cut_text(self):
        """Cut selected text"""
        try:
            self.text_area.event_generate("<<Cut>>")
        except:
            pass
            
    def copy_text(self):
        """Copy selected text"""
        try:
            self.text_area.event_generate("<<Copy>>")
        except:
            pass
            
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            self.text_area.event_generate("<<Paste>>")
        except:
            pass
            
    def find_text(self):
        """Find text in the document"""
        search_text = simpledialog.askstring("Find", "Enter text to find:")
        if search_text:
            content = self.text_area.get(1.0, tk.END)
            start_pos = content.find(search_text)
            if start_pos != -1:
                # Convert to Tkinter index format
                lines_before = content[:start_pos].count('\n')
                char_pos = start_pos - content[:start_pos].rfind('\n') - 1
                start_index = f"{lines_before + 1}.{char_pos}"
                end_index = f"{lines_before + 1}.{char_pos + len(search_text)}"
                
                self.text_area.tag_remove("highlight", 1.0, tk.END)
                self.text_area.tag_add("highlight", start_index, end_index)
                self.text_area.tag_config("highlight", background="yellow")
                self.text_area.see(start_index)
                self.status_bar.config(text=f"Found: {search_text}")
            else:
                messagebox.showinfo("Find", f"Text '{search_text}' not found")
                
    def replace_text(self):
        """Replace text in the document"""
        search_text = simpledialog.askstring("Replace", "Enter text to find:")
        if search_text:
            replace_text = simpledialog.askstring("Replace", "Enter replacement text:")
            if replace_text is not None:
                content = self.text_area.get(1.0, tk.END)
                new_content = content.replace(search_text, replace_text)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, new_content)
                self.status_bar.config(text=f"Replaced '{search_text}' with '{replace_text}'")
                
    def run(self):
        """Start the text editor"""
        self.root.mainloop()

def open_text_editor():
    """Function to open the text editor"""
    editor = TextEditor()
    editor.run()

if __name__ == "__main__":
    open_text_editor()