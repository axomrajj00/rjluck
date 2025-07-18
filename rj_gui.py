#!/usr/bin/env python3
"""
RJ GUI - Advanced Visual Interface for RJ Assistant
Features: JARVIS-style interface, animations, console, memory display
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import io
import base64

class RJInterface:
    def __init__(self, rj_assistant):
        self.rj_assistant = rj_assistant
        self.root = tk.Tk()
        self.setup_main_window()
        self.setup_styles()
        self.create_jarvis_face()
        self.setup_ui_components()
        self.animation_running = True
        self.start_animations()

    def setup_main_window(self):
        """Setup main window with JARVIS theme"""
        self.root.title("RJ - Advanced AI Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Set window icon if available
        try:
            # Create a simple icon
            icon_data = self.create_rj_icon()
            self.root.iconphoto(True, icon_data)
        except:
            pass

    def create_rj_icon(self):
        """Create RJ icon programmatically"""
        # Create a 64x64 icon
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw circular background
        draw.ellipse([4, 4, 60, 60], fill='#00ffff', outline='#ffffff', width=2)
        
        # Draw "RJ" text
        try:
            # Simple text representation
            draw.text((18, 20), "RJ", fill='#000000', anchor="mm")
        except:
            pass
        
        return ImageTk.PhotoImage(img)

    def setup_styles(self):
        """Setup color scheme and styles"""
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'accent_blue': '#00ccff',
            'accent_cyan': '#00ffff',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'success': '#00ff00',
            'warning': '#ffaa00',
            'error': '#ff4444'
        }

    def create_jarvis_face(self):
        """Create animated JARVIS-style face"""
        self.face_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.face_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Create canvas for face animation
        self.face_canvas = tk.Canvas(
            self.face_frame, 
            width=400, 
            height=200, 
            bg=self.colors['bg_primary'],
            highlightthickness=0
        )
        self.face_canvas.pack(pady=10)
        
        self.draw_jarvis_face()

    def draw_jarvis_face(self):
        """Draw JARVIS-style animated face"""
        self.face_canvas.delete("all")
        
        # Center coordinates
        cx, cy = 200, 100
        
        # Draw outer circle (head outline)
        self.face_canvas.create_oval(
            cx-80, cy-80, cx+80, cy+80,
            outline=self.colors['accent_cyan'],
            width=2
        )
        
        # Draw inner circles (eyes)
        eye_y = cy - 20
        self.face_canvas.create_oval(
            cx-40, eye_y-15, cx-20, eye_y+15,
            fill=self.colors['accent_blue'],
            outline=self.colors['accent_cyan']
        )
        self.face_canvas.create_oval(
            cx+20, eye_y-15, cx+40, eye_y+15,
            fill=self.colors['accent_blue'],
            outline=self.colors['accent_cyan']
        )
        
        # Draw mouth (speaking indicator)
        mouth_y = cy + 30
        current_time = time.time()
        mouth_width = 40 + 10 * np.sin(current_time * 4)  # Animated width
        self.face_canvas.create_arc(
            cx-mouth_width/2, mouth_y-10, cx+mouth_width/2, mouth_y+10,
            start=0, extent=180,
            outline=self.colors['accent_cyan'],
            width=2
        )
        
        # Draw status text
        status = "LISTENING" if hasattr(self.rj_assistant, 'listening') and self.rj_assistant.listening else "READY"
        self.face_canvas.create_text(
            cx, cy+70,
            text=f"RJ - {status}",
            fill=self.colors['accent_cyan'],
            font=('Courier', 12, 'bold')
        )
        
        # Schedule next frame
        if self.animation_running:
            self.root.after(100, self.draw_jarvis_face)

    def setup_ui_components(self):
        """Setup all UI components"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Console and Memory
        left_panel = tk.Frame(main_container, bg=self.colors['bg_secondary'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel - Tasks and Controls
        right_panel = tk.Frame(main_container, bg=self.colors['bg_secondary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        self.setup_console(left_panel)
        self.setup_memory_display(left_panel)
        self.setup_task_manager(right_panel)
        self.setup_controls(right_panel)

    def setup_console(self, parent):
        """Setup console output area"""
        console_frame = tk.LabelFrame(
            parent, 
            text="🖥️ Console Output", 
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Courier', 10, 'bold')
        )
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.console_text = scrolledtext.ScrolledText(
            console_frame,
            bg=self.colors['bg_primary'],
            fg=self.colors['accent_cyan'],
            font=('Courier', 10),
            wrap=tk.WORD,
            height=15
        )
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add initial message
        self.log_to_console("🎙️ RJ Assistant GUI Initialized", "success")

    def setup_memory_display(self, parent):
        """Setup memory display area"""
        memory_frame = tk.LabelFrame(
            parent,
            text="🧠 Memory Bank",
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Courier', 10, 'bold')
        )
        memory_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.memory_text = scrolledtext.ScrolledText(
            memory_frame,
            bg=self.colors['bg_primary'],
            fg=self.colors['accent_blue'],
            font=('Courier', 9),
            wrap=tk.WORD,
            height=8
        )
        self.memory_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.refresh_memory_display()

    def setup_task_manager(self, parent):
        """Setup task management area"""
        task_frame = tk.LabelFrame(
            parent,
            text="⏱️ Task Manager",
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Courier', 10, 'bold')
        )
        task_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Task list
        self.task_listbox = tk.Listbox(
            task_frame,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            font=('Courier', 9),
            selectbackground=self.colors['accent_blue']
        )
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Task controls
        task_controls = tk.Frame(task_frame, bg=self.colors['bg_secondary'])
        task_controls.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        tk.Button(
            task_controls,
            text="Complete Task",
            command=self.complete_selected_task,
            bg=self.colors['success'],
            fg='black',
            font=('Courier', 8, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            task_controls,
            text="Remove Task",
            command=self.remove_selected_task,
            bg=self.colors['error'],
            fg='white',
            font=('Courier', 8, 'bold')
        ).pack(side=tk.LEFT)

    def setup_controls(self, parent):
        """Setup control buttons"""
        controls_frame = tk.LabelFrame(
            parent,
            text="🎛️ Controls",
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Courier', 10, 'bold')
        )
        controls_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Status display
        self.status_label = tk.Label(
            controls_frame,
            text="Status: Ready",
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent_cyan'],
            font=('Courier', 9, 'bold')
        )
        self.status_label.pack(pady=5)
        
        # Control buttons
        tk.Button(
            controls_frame,
            text="🎤 Start Listening",
            command=self.start_listening,
            bg=self.colors['accent_blue'],
            fg='black',
            font=('Courier', 8, 'bold'),
            width=15
        ).pack(pady=2)
        
        tk.Button(
            controls_frame,
            text="🔇 Stop Listening",
            command=self.stop_listening,
            bg=self.colors['warning'],
            fg='black',
            font=('Courier', 8, 'bold'),
            width=15
        ).pack(pady=2)
        
        tk.Button(
            controls_frame,
            text="🧠 Clear Memory",
            command=self.clear_memory,
            bg=self.colors['error'],
            fg='white',
            font=('Courier', 8, 'bold'),
            width=15
        ).pack(pady=2)
        
        tk.Button(
            controls_frame,
            text="📋 Export Logs",
            command=self.export_logs,
            bg=self.colors['accent_cyan'],
            fg='black',
            font=('Courier', 8, 'bold'),
            width=15
        ).pack(pady=2)

    def log_to_console(self, message, msg_type="info"):
        """Log message to console with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "info": self.colors['text_primary'],
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['error'],
            "system": self.colors['accent_cyan']
        }
        
        color = color_map.get(msg_type, self.colors['text_primary'])
        
        self.console_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console_text.see(tk.END)
        
        # Color the last line
        last_line = self.console_text.index(tk.END + "-2l")
        self.console_text.tag_add(msg_type, last_line, tk.END)
        self.console_text.tag_config(msg_type, foreground=color)

    def refresh_memory_display(self):
        """Refresh memory display from JSON file"""
        try:
            with open('rj_memory.json', 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            self.memory_text.delete(1.0, tk.END)
            
            if memory_data.get('memories'):
                for i, memory in enumerate(memory_data['memories'], 1):
                    timestamp = memory.get('timestamp', 'Unknown')
                    content = memory.get('content', '')
                    memory_type = memory.get('type', 'note')
                    
                    self.memory_text.insert(tk.END, f"{i}. [{timestamp}] ({memory_type})\n")
                    self.memory_text.insert(tk.END, f"   {content}\n\n")
            else:
                self.memory_text.insert(tk.END, "No memories stored yet...")
                
        except FileNotFoundError:
            self.memory_text.delete(1.0, tk.END)
            self.memory_text.insert(tk.END, "Memory file not found. Will be created when first memory is stored.")

    def refresh_task_display(self):
        """Refresh task display from JSON file"""
        try:
            with open('rj_memory.json', 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            self.task_listbox.delete(0, tk.END)
            
            if memory_data.get('tasks'):
                for task in memory_data['tasks']:
                    status = "✅" if task.get('completed') else "⏳"
                    timer_info = ""
                    if task.get('timer_end'):
                        remaining = task['timer_end'] - time.time()
                        if remaining > 0:
                            timer_info = f" (⏰ {int(remaining)}s)"
                    
                    display_text = f"{status} {task['description']}{timer_info}"
                    self.task_listbox.insert(tk.END, display_text)
                    
        except FileNotFoundError:
            pass

    def complete_selected_task(self):
        """Mark selected task as completed"""
        selection = self.task_listbox.curselection()
        if selection:
            task_index = selection[0]
            # Update task in memory
            self.rj_assistant.complete_task(task_index)
            self.refresh_task_display()
            self.log_to_console(f"Task {task_index + 1} marked as completed", "success")

    def remove_selected_task(self):
        """Remove selected task"""
        selection = self.task_listbox.curselection()
        if selection:
            task_index = selection[0]
            # Remove task from memory
            self.rj_assistant.remove_task(task_index)
            self.refresh_task_display()
            self.log_to_console(f"Task {task_index + 1} removed", "warning")

    def start_listening(self):
        """Start voice listening in background thread"""
        def listen_thread():
            self.log_to_console("🎤 Voice listening started...", "system")
            self.status_label.config(text="Status: Listening...")
            if hasattr(self.rj_assistant, 'start_listening'):
                self.rj_assistant.start_listening()
        
        threading.Thread(target=listen_thread, daemon=True).start()

    def stop_listening(self):
        """Stop voice listening"""
        self.log_to_console("🔇 Voice listening stopped", "warning")
        self.status_label.config(text="Status: Stopped")
        if hasattr(self.rj_assistant, 'stop_listening'):
            self.rj_assistant.stop_listening()

    def clear_memory(self):
        """Clear all memories"""
        self.rj_assistant.clear_all_memories()
        self.refresh_memory_display()
        self.log_to_console("🧠 All memories cleared", "warning")

    def export_logs(self):
        """Export console logs to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rj_logs_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("RJ Assistant - Console Logs\n")
            f.write("=" * 50 + "\n\n")
            f.write(self.console_text.get(1.0, tk.END))
        
        self.log_to_console(f"📋 Logs exported to {filename}", "success")

    def start_animations(self):
        """Start all animations"""
        self.animation_running = True

    def stop_animations(self):
        """Stop all animations"""
        self.animation_running = False

    def update_status(self, status):
        """Update status display"""
        self.status_label.config(text=f"Status: {status}")

    def run(self):
        """Start the GUI"""
        try:
            self.root.mainloop()
        finally:
            self.stop_animations()

def create_gui_for_rj(rj_assistant):
    """Create and return GUI instance"""
    return RJInterface(rj_assistant)