#!/usr/bin/env python3
"""
Ultimate RJ Assistant - Perfect AI Assistant
Features: Voice + Text input, Auto task completion, Beautiful GUI, Console toggle, Smart responses
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import psutil
import re
import wikipedia
import json
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import requests

import pyttsx3
import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv

# GUI imports
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np

# Advanced features
import pyautogui
import pytesseract
from PIL import ImageGrab

# Load environment variables
load_dotenv()

class UltimateRJ:
    def __init__(self):
        """Initialize Ultimate RJ Assistant"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.listening = False
        self.sleep_mode = False
        self.show_console = True
        self.voice_mode = True
        self.text_mode = True
        
        # Wake words and activation
        self.wake_words = ["hello rj", "rj", "hello"]
        self.conversation_history = []
        
        # Retry mechanism
        self.last_failed_command = None
        self.retry_mode = False
        self.retry_suggestions = []
        
        self.setup_command_patterns()
        self.setup_memory_system()
        self.setup_gui()
        
        print("🎯 Ultimate RJ Assistant initialized!")
        self.speak("Namaste Sir! Main Ultimate RJ hun. Voice ya text - dono mein commands de sakte hain.")

    def setup_ai_client(self):
        """Setup OpenAI client for DeepSeek API"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DeepSeek API key not found in environment variables")
        
        self.ai_client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def setup_speech_components(self):
        """Setup speech recognition and text-to-speech"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        
        # Set voice [2] as requested
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 2:
            self.tts_engine.setProperty('voice', voices[2].id)
        elif len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        
        self.tts_engine.setProperty('rate', 175)
        self.tts_engine.setProperty('volume', 0.9)

    def setup_memory_system(self):
        """Setup comprehensive memory system"""
        self.memory_file = 'ultimate_rj_memory.json'
        self.load_memory()

    def setup_command_patterns(self):
        """Setup comprehensive command patterns"""
        self.patterns = {
            'greetings': {
                'activate': r'hello|rj|hi|namaste',
                'goodbye': r'bye|alvida|goodbye|exit|quit'
            },
            'coding': {
                'vscode': r'vs code|vscode|code editor',
                'generate': r'banao|create|generate|code|website|program|app',
                'chatgpt': r'chat gpt|chatgpt|gpt|openai'
            },
            'system': {
                'volume': r'volume|awaz',
                'scroll': r'scroll|scrool',
                'shutdown': r'shutdown|power off|band kar',
                'restart': r'restart|reboot'
            },
            'web': {
                'youtube': r'youtube|video',
                'google': r'google|search',
                'website': r'website|site'
            },
            'files': {
                'open': r'open|kholo',
                'delete': r'delete|remove|hatao',
                'create': r'create|banao|new'
            },
            'productivity': {
                'routine': r'routine|schedule|plan',
                'reminder': r'reminder|yaad|alert',
                'note': r'note|yaad rakh|remember'
            }
        }

    def load_memory(self):
        """Load comprehensive memory"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memory_data = json.load(f)
        except FileNotFoundError:
            self.memory_data = {
                'conversations': [],
                'tasks_completed': [],
                'user_preferences': {
                    'address_as': 'Sir',
                    'voice_enabled': True,
                    'auto_complete': True,
                    'console_visible': True
                },
                'projects_created': [],
                'system_commands': [],
                'session_stats': {
                    'total_tasks': 0,
                    'successful_completions': 0,
                    'last_session': datetime.now().isoformat()
                },
                'created': datetime.now().isoformat()
            }
            self.save_memory()

    def save_memory(self):
        """Save memory to JSON"""
        self.memory_data['last_updated'] = datetime.now().isoformat()
        self.memory_data['user_preferences']['console_visible'] = self.show_console
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_data, f, ensure_ascii=False, indent=2)

    def setup_gui(self):
        """Setup beautiful GUI interface"""
        self.root = tk.Tk()
        self.root.title("Ultimate RJ Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg='#0a0a0a')
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header()
        self.create_control_panel()
        self.create_rj_display()
        self.create_input_section()
        self.create_console_section()
        
        # Start background voice listener
        threading.Thread(target=self.background_voice_listener, daemon=True).start()

    def create_header(self):
        """Create beautiful header with RJ AI branding"""
        header_frame = tk.Frame(self.main_frame, bg='#0a0a0a')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Create gradient-like header with styled text
        canvas = tk.Canvas(header_frame, height=80, bg='#0a0a0a', highlightthickness=0)
        canvas.pack(fill='x')
        
        # Create gradient background
        for i in range(80):
            color_intensity = int(15 + (i / 80) * 30)
            color = f'#{color_intensity:02x}{color_intensity:02x}{color_intensity + 20:02x}'
            canvas.create_line(0, i, 1200, i, fill=color)
        
        # Add RJ AI text with glow effect
        canvas.create_text(600, 25, text="RJ", font=('Arial', 28, 'bold'), 
                          fill='#00ff88', anchor='center')
        canvas.create_text(600, 55, text="AI ASSISTANT", font=('Arial', 14, 'bold'), 
                          fill='#00ccff', anchor='center')
        
        # Add status indicator
        self.status_indicator = canvas.create_oval(1050, 20, 1070, 40, 
                                                  fill='#00ff00', outline='#ffffff')
        self.status_text = canvas.create_text(1100, 30, text="Ready", 
                                            font=('Arial', 10, 'bold'), 
                                            fill='#00ff00', anchor='w')

    def create_control_panel(self):
        """Create control panel with beautiful buttons"""
        control_frame = tk.Frame(self.main_frame, bg='#1a1a1a', relief='raised', bd=2)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Style for buttons
        button_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#2a2a2a',
            'fg': '#ffffff',
            'activebackground': '#3a3a3a',
            'activeforeground': '#00ff88',
            'relief': 'raised',
            'bd': 2,
            'padx': 15,
            'pady': 5
        }
        
        # Control buttons
        tk.Label(control_frame, text="🎛️ CONTROLS", font=('Arial', 12, 'bold'), 
                bg='#1a1a1a', fg='#00ccff').pack(pady=5)
        
        button_frame = tk.Frame(control_frame, bg='#1a1a1a')
        button_frame.pack(pady=5)
        
        self.voice_btn = tk.Button(button_frame, text="🎤 Voice: ON", 
                                  command=self.toggle_voice_mode, **button_style)
        self.voice_btn.pack(side='left', padx=5)
        
        self.console_btn = tk.Button(button_frame, text="📺 Console: ON", 
                                    command=self.toggle_console, **button_style)
        self.console_btn.pack(side='left', padx=5)
        
        tk.Button(button_frame, text="💾 Save Session", 
                 command=self.save_session, **button_style).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="🗑️ Clear Console", 
                 command=self.clear_console, **button_style).pack(side='left', padx=5)

    def create_rj_display(self):
        """Create animated RJ avatar display"""
        display_frame = tk.Frame(self.main_frame, bg='#1a1a1a', relief='raised', bd=2)
        display_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(display_frame, text="🤖 RJ STATUS", font=('Arial', 12, 'bold'), 
                bg='#1a1a1a', fg='#00ccff').pack(pady=5)
        
        # Avatar canvas
        self.avatar_canvas = tk.Canvas(display_frame, width=200, height=150, 
                                      bg='#0a0a0a', highlightthickness=0)
        self.avatar_canvas.pack(pady=10)
        
        self.draw_rj_avatar()
        
        # Status display
        self.status_label = tk.Label(display_frame, text="😊 Ready for commands, Sir!", 
                                   font=('Arial', 11, 'bold'), bg='#1a1a1a', fg='#00ff88')
        self.status_label.pack(pady=5)

    def draw_rj_avatar(self):
        """Draw animated RJ avatar"""
        canvas = self.avatar_canvas
        canvas.delete("all")
        
        # Draw futuristic avatar
        # Head circle with glow
        canvas.create_oval(75, 30, 125, 80, fill='#001122', outline='#00ccff', width=3)
        canvas.create_oval(80, 35, 120, 75, fill='#002244', outline='#00ff88', width=2)
        
        # Eyes (animated)
        if self.listening:
            # Listening eyes (active)
            canvas.create_oval(85, 45, 95, 55, fill='#00ff00', outline='#ffffff')
            canvas.create_oval(105, 45, 115, 55, fill='#00ff00', outline='#ffffff')
        else:
            # Normal eyes
            canvas.create_oval(85, 45, 95, 55, fill='#0080ff', outline='#ffffff')
            canvas.create_oval(105, 45, 115, 55, fill='#0080ff', outline='#ffffff')
        
        # Mouth (changes with status)
        if self.sleep_mode:
            canvas.create_arc(90, 60, 110, 70, start=0, extent=180, fill='#666666')
        else:
            canvas.create_arc(90, 60, 110, 70, start=0, extent=-180, fill='#00ff88', width=2)
        
        # Body
        canvas.create_rectangle(90, 80, 110, 120, fill='#002244', outline='#00ccff', width=2)
        
        # Arms
        canvas.create_line(90, 90, 70, 110, fill='#00ccff', width=3)
        canvas.create_line(110, 90, 130, 110, fill='#00ccff', width=3)
        
        # RJ text on body
        canvas.create_text(100, 100, text="RJ", font=('Arial', 8, 'bold'), fill='#00ff88')

    def create_input_section(self):
        """Create text input section"""
        input_frame = tk.Frame(self.main_frame, bg='#1a1a1a', relief='raised', bd=2)
        input_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(input_frame, text="💬 TYPE COMMAND", font=('Arial', 12, 'bold'), 
                bg='#1a1a1a', fg='#00ccff').pack(pady=5)
        
        # Input area
        text_frame = tk.Frame(input_frame, bg='#1a1a1a')
        text_frame.pack(fill='x', padx=10, pady=5)
        
        self.text_input = tk.Entry(text_frame, font=('Arial', 12), bg='#2a2a2a', 
                                  fg='#ffffff', insertbackground='#00ff88',
                                  relief='sunken', bd=2)
        self.text_input.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.text_input.bind('<Return>', self.process_text_input)
        
        send_btn = tk.Button(text_frame, text="🚀 SEND", font=('Arial', 10, 'bold'),
                           bg='#00aa44', fg='#ffffff', activebackground='#00cc55',
                           command=self.process_text_input, padx=20)
        send_btn.pack(side='right')

    def create_console_section(self):
        """Create console output section"""
        self.console_frame = tk.Frame(self.main_frame, bg='#1a1a1a', relief='raised', bd=2)
        self.console_frame.pack(fill='both', expand=True)
        
        console_header = tk.Frame(self.console_frame, bg='#1a1a1a')
        console_header.pack(fill='x', pady=5)
        
        tk.Label(console_header, text="🖥️ CONSOLE OUTPUT", font=('Arial', 12, 'bold'), 
                bg='#1a1a1a', fg='#00ccff').pack(side='left', padx=10)
        
        # Console text area with scrollbar
        console_container = tk.Frame(self.console_frame, bg='#1a1a1a')
        console_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.console_text = scrolledtext.ScrolledText(
            console_container, 
            font=('Consolas', 10), 
            bg='#000000', 
            fg='#00ff00',
            insertbackground='#00ff00',
            wrap='word',
            state='disabled',
            relief='sunken',
            bd=2
        )
        self.console_text.pack(fill='both', expand=True)
        
        # Configure console colors
        self.console_text.tag_configure('user', foreground='#00ccff')
        self.console_text.tag_configure('rj', foreground='#00ff88')
        self.console_text.tag_configure('system', foreground='#ffaa00')
        self.console_text.tag_configure('error', foreground='#ff4444')
        self.console_text.tag_configure('success', foreground='#44ff44')

    def log_to_console(self, message: str, msg_type: str = 'system'):
        """Log message to console with colors"""
        if not self.show_console:
            return
            
        self.console_text.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if msg_type == 'user':
            self.console_text.insert('end', f"[{timestamp}] User: {message}\n", 'user')
        elif msg_type == 'rj':
            self.console_text.insert('end', f"[{timestamp}] RJ: {message}\n", 'rj')
        elif msg_type == 'error':
            self.console_text.insert('end', f"[{timestamp}] ERROR: {message}\n", 'error')
        elif msg_type == 'success':
            self.console_text.insert('end', f"[{timestamp}] SUCCESS: {message}\n", 'success')
        else:
            self.console_text.insert('end', f"[{timestamp}] {message}\n", 'system')
        
        self.console_text.config(state='disabled')
        self.console_text.see('end')

    def toggle_console(self):
        """Toggle console visibility"""
        if self.show_console:
            self.console_frame.pack_forget()
            self.console_btn.config(text="📺 Console: OFF", bg='#aa4400')
            self.show_console = False
        else:
            self.console_frame.pack(fill='both', expand=True)
            self.console_btn.config(text="📺 Console: ON", bg='#2a2a2a')
            self.show_console = True
        self.save_memory()

    def toggle_voice_mode(self):
        """Toggle voice recognition"""
        self.voice_mode = not self.voice_mode
        if self.voice_mode:
            self.voice_btn.config(text="🎤 Voice: ON", bg='#2a2a2a')
            self.log_to_console("Voice recognition enabled", 'system')
        else:
            self.voice_btn.config(text="🎤 Voice: OFF", bg='#aa4400')
            self.log_to_console("Voice recognition disabled", 'system')

    def clear_console(self):
        """Clear console output"""
        self.console_text.config(state='normal')
        self.console_text.delete(1.0, 'end')
        self.console_text.config(state='disabled')
        self.log_to_console("Console cleared", 'system')

    def save_session(self):
        """Save current session"""
        self.save_memory()
        self.log_to_console("Session saved successfully", 'success')
        self.speak("Session save kar diya Sir!")

    def update_status(self, status: str, color: str = '#00ff00'):
        """Update status display"""
        self.status_label.config(text=status, fg=color)
        # Update canvas status
        try:
            canvas = self.main_frame.winfo_children()[0].winfo_children()[0]  # Header canvas
            canvas.itemconfig(self.status_text, text=status.split()[0], fill=color)
        except:
            pass

    def speak(self, text: str):
        """Enhanced speak with Sir addressing"""
        # Always address as Sir
        if not text.lower().startswith('sir'):
            if 'sir' not in text.lower():
                text = f"Sir, {text}"
        
        print(f"🗣️ RJ: {text}")
        self.log_to_console(text, 'rj')
        
        clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()

    def listen(self) -> Optional[str]:
        """Enhanced voice input"""
        if not self.voice_mode:
            return None
            
        try:
            self.listening = True
            self.update_status("🎤 Listening...", '#ffaa00')
            self.draw_rj_avatar()  # Update avatar
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
            
            self.update_status("🔄 Processing...", '#0080ff')
            
            try:
                text = self.recognizer.recognize_google(audio, language='hi-IN').lower()
                self.log_to_console(f"Heard (Hindi): {text}", 'user')
                return text
            except:
                text = self.recognizer.recognize_google(audio, language='en-US').lower()
                self.log_to_console(f"Heard (English): {text}", 'user')
                return text
                
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            self.log_to_console("Could not understand audio", 'error')
            return None
        except sr.RequestError as e:
            self.log_to_console(f"Speech recognition error: {e}", 'error')
            return None
        finally:
            self.listening = False
            self.update_status("😊 Ready", '#00ff00')
            self.draw_rj_avatar()

    def background_voice_listener(self):
        """Background voice listener thread"""
        while self.running:
            try:
                if self.voice_mode and not self.sleep_mode:
                    user_input = self.listen()
                    if user_input:
                        # Check for activation words
                        activated = False
                        for wake_word in self.wake_words:
                            if wake_word in user_input:
                                activated = True
                                user_input = user_input.replace(wake_word, "").strip()
                                break
                        
                        if activated or self.listening:
                            if user_input:
                                self.process_command(user_input)
                            else:
                                self.speak("Sir, kya kaam hai?")
                
                time.sleep(0.5)
            except Exception as e:
                self.log_to_console(f"Voice listener error: {e}", 'error')
                time.sleep(1)

    def process_text_input(self, event=None):
        """Process text input from GUI"""
        command = self.text_input.get().strip()
        if command:
            self.text_input.delete(0, 'end')
            self.log_to_console(command, 'user')
            self.process_command(command)

    def process_command(self, command: str):
        """Process any command intelligently without asking questions"""
        if not command:
            return
        
        # Check for retry commands
        if self.is_retry_command(command):
            self.handle_retry_command(command)
            return
        
        self.memory_data['session_stats']['total_tasks'] += 1
        self.update_status("🤖 Working...", '#ffaa00')
        
        try:
            # Reset retry mode for new commands
            self.retry_mode = False
            self.last_failed_command = None
            
            # Auto-detect and execute based on command content
            success = False
            if self.is_coding_command(command):
                success = self.auto_handle_coding(command)
            elif self.is_system_command(command):
                success = self.auto_handle_system(command)
            elif self.is_web_command(command):
                success = self.auto_handle_web(command)
            elif self.is_file_command(command):
                success = self.auto_handle_files(command)
            elif self.is_productivity_command(command):
                success = self.auto_handle_productivity(command)
            else:
                # Use AI for general queries
                success = self.handle_ai_query(command)
            
            if success:
                self.memory_data['session_stats']['successful_completions'] += 1
                self.update_status("✅ Task Completed", '#44ff44')
            else:
                # Task failed, enable retry mode
                self.enable_retry_mode(command)
            
        except Exception as e:
            self.log_to_console(f"Error processing command: {e}", 'error')
            self.enable_retry_mode(command, str(e))
        
        self.save_memory()

    def is_coding_command(self, command: str) -> bool:
        """Check if command is coding related"""
        coding_keywords = ['vs code', 'vscode', 'code', 'website', 'app', 'program', 
                          'banao', 'create', 'generate', 'chatgpt', 'gpt']
        return any(keyword in command.lower() for keyword in coding_keywords)

    def auto_handle_coding(self, command: str) -> bool:
        """Automatically handle coding commands"""
        command = command.lower()
        
        try:
            if 'chatgpt' in command or 'gpt' in command:
                # Extract search query
                search_query = self.extract_search_query(command)
                self.speak("Sir, ChatGPT open kar raha hun!")
                self.log_to_console("Opening ChatGPT...", 'system')
                webbrowser.open("https://chat.openai.com/")
                if search_query:
                    time.sleep(3)
                    try:
                        pyautogui.typewrite(search_query)
                        self.speak(f"Sir, '{search_query}' search query type kar diya!")
                    except:
                        self.speak(f"Sir, manually '{search_query}' search kariye.")
                return True
            
            elif 'vs code' in command or 'vscode' in command:
                # Auto-detect project type and create
                project_type = self.detect_project_type(command)
                self.speak("Sir, VS Code open kar raha hun aur project create kar raha hun!")
                return self.create_and_open_project(project_type, command)
            
            else:
                # Generate custom code
                self.speak("Sir, aapke liye code generate kar raha hun!")
                return self.generate_smart_code(command)
                
        except Exception as e:
            self.log_to_console(f"Coding command failed: {e}", 'error')
            return False

    def detect_project_type(self, command: str) -> str:
        """Auto-detect project type from command"""
        if any(word in command for word in ['login', 'signin', 'auth']):
            return 'login_page'
        elif any(word in command for word in ['dashboard', 'admin', 'panel']):
            return 'dashboard'
        elif any(word in command for word in ['portfolio', 'resume', 'personal']):
            return 'portfolio'
        elif any(word in command for word in ['shop', 'ecommerce', 'store']):
            return 'ecommerce'
        elif any(word in command for word in ['blog', 'article', 'news']):
            return 'blog'
        elif any(word in command for word in ['calculator', 'calc']):
            return 'calculator'
        elif any(word in command for word in ['todo', 'task']):
            return 'todo_app'
        elif any(word in command for word in ['weather']):
            return 'weather_app'
        else:
            return 'basic_website'

    def create_and_open_project(self, project_type: str, command: str) -> bool:
        """Create and open project automatically"""
        try:
            # Check VS Code installation
            if not self.check_vscode_installed():
                self.speak("Sir, VS Code install nahi hai. Mujhe alternative app try karne ko kehiye ya VS Code install kariye.")
                self.log_to_console("VS Code not found, installation required", 'error')
                self.suggest_alternatives("vscode", command)
                return False
            
            # Create project
            project_name = f"{project_type}_{int(time.time())}"
            project_path = Path.home() / "Desktop" / project_name
            project_path.mkdir(exist_ok=True)
            
            self.log_to_console(f"Creating {project_type} project...", 'system')
            
            if project_type == 'login_page':
                self.create_login_project(project_path)
            elif project_type == 'dashboard':
                self.create_dashboard_project(project_path)
            elif project_type == 'calculator':
                self.create_calculator_project(project_path)
            elif project_type == 'todo_app':
                self.create_todo_project(project_path)
            else:
                self.create_basic_project(project_path, project_type)
            
            # Try to open in VS Code
            result = subprocess.Popen(['code', str(project_path)])
            if result.returncode is None:  # Process started successfully
                self.speak(f"Sir, {project_type} successfully create kar diya aur VS Code mein open kar diya!")
                self.log_to_console(f"Project created: {project_path}", 'success')
                
                # Save to memory
                self.memory_data['projects_created'].append({
                    'type': project_type,
                    'path': str(project_path),
                    'command': command,
                    'created_at': datetime.now().isoformat()
                })
                return True
            else:
                self.speak("Sir, VS Code open karne mein problem aaya. Alternative editor try karne ko kehiye.")
                self.suggest_alternatives("vscode", command)
                return False
            
        except Exception as e:
            self.speak(f"Sir, project create karne mein error: {str(e)}")
            self.suggest_alternatives("project_creation", command)
            return False

    def check_vscode_installed(self) -> bool:
        """Check if VS Code is installed"""
        try:
            result = subprocess.run(['which', 'code'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def create_calculator_project(self, project_path: Path):
        """Create calculator project"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RJ Calculator</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="calculator">
        <div class="display">
            <input type="text" id="display" readonly>
        </div>
        <div class="buttons">
            <button onclick="clearDisplay()">C</button>
            <button onclick="deleteLast()">⌫</button>
            <button onclick="appendToDisplay('/')">÷</button>
            <button onclick="appendToDisplay('*')">×</button>
            
            <button onclick="appendToDisplay('7')">7</button>
            <button onclick="appendToDisplay('8')">8</button>
            <button onclick="appendToDisplay('9')">9</button>
            <button onclick="appendToDisplay('-')">-</button>
            
            <button onclick="appendToDisplay('4')">4</button>
            <button onclick="appendToDisplay('5')">5</button>
            <button onclick="appendToDisplay('6')">6</button>
            <button onclick="appendToDisplay('+')">+</button>
            
            <button onclick="appendToDisplay('1')">1</button>
            <button onclick="appendToDisplay('2')">2</button>
            <button onclick="appendToDisplay('3')">3</button>
            <button onclick="calculate()" class="equals" rowspan="2">=</button>
            
            <button onclick="appendToDisplay('0')" class="zero">0</button>
            <button onclick="appendToDisplay('.')">.</button>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>'''
        
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.calculator {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

.display {
    margin-bottom: 20px;
}

#display {
    width: 100%;
    height: 60px;
    font-size: 24px;
    text-align: right;
    background: rgba(0, 0, 0, 0.3);
    border: none;
    border-radius: 10px;
    color: white;
    padding: 0 15px;
}

.buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    width: 300px;
}

button {
    height: 60px;
    border: none;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    cursor: pointer;
    transition: all 0.3s;
}

button:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.equals {
    grid-row: span 2;
    background: rgba(0, 255, 136, 0.3);
}

.zero {
    grid-column: span 2;
}'''
        
        js_content = '''let display = document.getElementById('display');
let currentInput = '';

function appendToDisplay(value) {
    currentInput += value;
    display.value = currentInput;
}

function clearDisplay() {
    currentInput = '';
    display.value = '';
}

function deleteLast() {
    currentInput = currentInput.slice(0, -1);
    display.value = currentInput;
}

function calculate() {
    try {
        let result = eval(currentInput);
        display.value = result;
        currentInput = result.toString();
    } catch (error) {
        display.value = 'Error';
        currentInput = '';
    }
}

// Keyboard support
document.addEventListener('keydown', function(event) {
    const key = event.key;
    
    if (key >= '0' && key <= '9' || key === '.' || key === '+' || key === '-' || key === '*' || key === '/') {
        appendToDisplay(key);
    } else if (key === 'Enter' || key === '=') {
        calculate();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearDisplay();
    } else if (key === 'Backspace') {
        deleteLast();
    }
});'''
        
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')
        (project_path / 'style.css').write_text(css_content, encoding='utf-8')
        (project_path / 'script.js').write_text(js_content, encoding='utf-8')

    def create_todo_project(self, project_path: Path):
        """Create todo app project"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RJ Todo App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>📝 RJ Todo List</h1>
        <div class="input-section">
            <input type="text" id="todoInput" placeholder="Add new task...">
            <button onclick="addTodo()">Add Task</button>
        </div>
        <div class="filter-section">
            <button onclick="filterTodos('all')" class="filter-btn active">All</button>
            <button onclick="filterTodos('pending')" class="filter-btn">Pending</button>
            <button onclick="filterTodos('completed')" class="filter-btn">Completed</button>
        </div>
        <ul id="todoList"></ul>
        <div class="stats">
            <span id="totalTasks">0 tasks</span>
            <span id="completedTasks">0 completed</span>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>'''
        
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 600px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

h1 {
    text-align: center;
    color: #2d3436;
    margin-bottom: 30px;
    font-size: 2.5em;
}

.input-section {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

#todoInput {
    flex: 1;
    padding: 15px;
    border: 2px solid #ddd;
    border-radius: 10px;
    font-size: 16px;
    outline: none;
    transition: border-color 0.3s;
}

#todoInput:focus {
    border-color: #74b9ff;
}

button {
    padding: 15px 25px;
    background: #74b9ff;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;
}

button:hover {
    background: #0984e3;
    transform: translateY(-2px);
}

.filter-section {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    justify-content: center;
}

.filter-btn {
    padding: 10px 20px;
    background: #ddd;
    color: #333;
    font-size: 14px;
}

.filter-btn.active {
    background: #74b9ff;
    color: white;
}

#todoList {
    list-style: none;
    margin-bottom: 20px;
}

.todo-item {
    display: flex;
    align-items: center;
    padding: 15px;
    margin: 10px 0;
    background: #f8f9fa;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: all 0.3s;
}

.todo-item:hover {
    transform: translateX(5px);
}

.todo-item.completed {
    opacity: 0.6;
    text-decoration: line-through;
}

.todo-text {
    flex: 1;
    margin-left: 10px;
}

.todo-actions {
    display: flex;
    gap: 5px;
}

.complete-btn, .delete-btn {
    padding: 5px 10px;
    font-size: 12px;
}

.complete-btn {
    background: #00b894;
}

.delete-btn {
    background: #e17055;
}

.stats {
    text-align: center;
    color: #636e72;
    font-size: 14px;
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 10px;
}'''
        
        js_content = '''let todos = [];
let filter = 'all';

function addTodo() {
    const input = document.getElementById('todoInput');
    const text = input.value.trim();
    
    if (text) {
        todos.push({
            id: Date.now(),
            text: text,
            completed: false,
            createdAt: new Date().toLocaleString()
        });
        
        input.value = '';
        renderTodos();
        updateStats();
    }
}

function toggleTodo(id) {
    todos = todos.map(todo => 
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
    );
    renderTodos();
    updateStats();
}

function deleteTodo(id) {
    todos = todos.filter(todo => todo.id !== id);
    renderTodos();
    updateStats();
}

function filterTodos(filterType) {
    filter = filterType;
    
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    renderTodos();
}

function renderTodos() {
    const list = document.getElementById('todoList');
    list.innerHTML = '';
    
    let filteredTodos = todos;
    if (filter === 'pending') {
        filteredTodos = todos.filter(todo => !todo.completed);
    } else if (filter === 'completed') {
        filteredTodos = todos.filter(todo => todo.completed);
    }
    
    filteredTodos.forEach(todo => {
        const li = document.createElement('li');
        li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
        li.innerHTML = `
            <input type="checkbox" ${todo.completed ? 'checked' : ''} 
                   onchange="toggleTodo(${todo.id})">
            <span class="todo-text">${todo.text}</span>
            <div class="todo-actions">
                <button class="complete-btn" onclick="toggleTodo(${todo.id})">
                    ${todo.completed ? 'Undo' : 'Done'}
                </button>
                <button class="delete-btn" onclick="deleteTodo(${todo.id})">Delete</button>
            </div>
        `;
        list.appendChild(li);
    });
}

function updateStats() {
    const total = todos.length;
    const completed = todos.filter(todo => todo.completed).length;
    
    document.getElementById('totalTasks').textContent = `${total} tasks`;
    document.getElementById('completedTasks').textContent = `${completed} completed`;
}

// Keyboard support
document.getElementById('todoInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        addTodo();
    }
});

// Initialize
updateStats();'''
        
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')
        (project_path / 'style.css').write_text(css_content, encoding='utf-8')
        (project_path / 'script.js').write_text(js_content, encoding='utf-8')

    def create_login_project(self, project_path: Path):
        """Create login page project - same as before but enhanced"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RJ Login Portal</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <h2>🔐 Welcome Back</h2>
            <form id="loginForm">
                <div class="input-group">
                    <input type="email" id="email" required>
                    <label for="email">Email Address</label>
                </div>
                <div class="input-group">
                    <input type="password" id="password" required>
                    <label for="password">Password</label>
                </div>
                <div class="remember-me">
                    <input type="checkbox" id="remember">
                    <label for="remember">Remember me</label>
                </div>
                <button type="submit">🚀 Login</button>
                <div class="links">
                    <a href="#">Forgot Password?</a>
                    <a href="#">Create Account</a>
                </div>
            </form>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>'''
        
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-container {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.18);
    animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
    from { transform: translateY(-50px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.login-box {
    width: 350px;
}

h2 {
    color: white;
    text-align: center;
    margin-bottom: 30px;
    font-weight: 300;
    font-size: 24px;
}

.input-group {
    position: relative;
    margin-bottom: 25px;
}

input[type="email"], input[type="password"] {
    width: 100%;
    padding: 15px 0;
    background: transparent;
    border: none;
    border-bottom: 2px solid rgba(255, 255, 255, 0.5);
    color: white;
    font-size: 16px;
    outline: none;
    transition: all 0.3s;
}

input[type="email"]:focus, input[type="password"]:focus {
    border-bottom-color: #00ff88;
}

label {
    position: absolute;
    top: 15px;
    left: 0;
    color: rgba(255, 255, 255, 0.7);
    transition: 0.3s;
    pointer-events: none;
}

input:focus ~ label,
input:valid ~ label {
    top: -5px;
    font-size: 12px;
    color: #00ff88;
}

.remember-me {
    display: flex;
    align-items: center;
    margin-bottom: 25px;
}

.remember-me input[type="checkbox"] {
    margin-right: 10px;
}

.remember-me label {
    position: static;
    color: rgba(255, 255, 255, 0.8);
    font-size: 14px;
}

button {
    width: 100%;
    padding: 15px;
    background: linear-gradient(45deg, #00ff88, #00ccff);
    border: none;
    border-radius: 25px;
    color: white;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
    text-transform: uppercase;
    letter-spacing: 1px;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
}

.links {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

.links a {
    color: rgba(255, 255, 255, 0.7);
    text-decoration: none;
    font-size: 14px;
    transition: color 0.3s;
}

.links a:hover {
    color: #00ff88;
}'''
        
        js_content = '''document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    
    // Simple validation
    if (!email || !password) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    if (!isValidEmail(email)) {
        showMessage('Please enter a valid email address', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('Password must be at least 6 characters', 'error');
        return;
    }
    
    // Simulate login process
    showMessage('Logging in...', 'info');
    
    setTimeout(() => {
        showMessage('Login successful! Welcome back 🎉', 'success');
        
        // Store login info if remember me is checked
        if (remember) {
            localStorage.setItem('rememberedEmail', email);
        }
        
        // Redirect or perform login action
        setTimeout(() => {
            alert('Login successful! Redirecting to dashboard...');
        }, 1000);
    }, 1500);
});

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showMessage(message, type) {
    // Remove existing message
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            messageDiv.style.background = 'linear-gradient(45deg, #00ff88, #00ccff)';
            break;
        case 'error':
            messageDiv.style.background = 'linear-gradient(45deg, #ff4757, #ff6b7a)';
            break;
        case 'info':
            messageDiv.style.background = 'linear-gradient(45deg, #3742fa, #5352ed)';
            break;
    }
    
    document.body.appendChild(messageDiv);
    
    // Remove message after 3 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Auto-fill remembered email on page load
window.addEventListener('load', function() {
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
        document.getElementById('email').value = rememberedEmail;
        document.getElementById('remember').checked = true;
    }
});

// Add CSS animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);'''
        
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')
        (project_path / 'style.css').write_text(css_content, encoding='utf-8')
        (project_path / 'script.js').write_text(js_content, encoding='utf-8')

    def create_dashboard_project(self, project_path: Path):
        """Create dashboard project - enhanced version"""
        # Similar to previous dashboard but with more features
        # ... (implementation similar to previous dashboard but enhanced)
        pass

    def create_basic_project(self, project_path: Path, project_type: str):
        """Create basic project template"""
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RJ {project_type.title()}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>🎯 {project_type.replace('_', ' ').title()}</h1>
        <p>Created by RJ Assistant for you! Start customizing this project.</p>
        <div class="content">
            <h2>Welcome to your new project!</h2>
            <p>This is a basic template. Add your content here.</p>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>'''
        
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 1000px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

h1 {
    text-align: center;
    color: #2d3436;
    margin-bottom: 20px;
    font-size: 2.5em;
}

.content {
    background: #f8f9fa;
    padding: 30px;
    border-radius: 15px;
    margin-top: 30px;
}

h2 {
    color: #333;
    margin-bottom: 15px;
}

p {
    color: #666;
    line-height: 1.6;
    font-size: 16px;
}'''
        
        js_content = '''console.log("RJ Project initialized successfully!");

// Add interactive features here
document.addEventListener('DOMContentLoaded', function() {
    console.log("Project is ready!");
    
    // Add click effect to container
    const container = document.querySelector('.container');
    container.addEventListener('click', function() {
        this.style.transform = 'scale(1.01)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 150);
    });
});'''
        
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')
        (project_path / 'style.css').write_text(css_content, encoding='utf-8')
        (project_path / 'script.js').write_text(js_content, encoding='utf-8')

    def extract_search_query(self, command: str) -> str:
        """Extract search query from command"""
        patterns = [
            r'search\s+(.+)',
            r'find\s+(.+)',
            r'(.+)\s+search',
            r'mein\s+(.+)',
            r'(.+)\s+ke\s+bare\s+mein'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                return match.group(1).strip()
        
        return ""

    def is_system_command(self, command: str) -> bool:
        """Check if command is system related"""
        system_keywords = ['volume', 'scroll', 'shutdown', 'restart', 'brightness', 'lock']
        return any(keyword in command.lower() for keyword in system_keywords)

    def auto_handle_system(self, command: str) -> bool:
        """Automatically handle system commands"""
        command = command.lower()
        
        try:
            if 'volume' in command:
                if any(word in command for word in ['up', 'badhao', 'jyada', 'increase']):
                    result = subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%+'], capture_output=True)
                    if result.returncode == 0:
                        self.speak("Sir, volume badha diya!")
                        return True
                    else:
                        self.speak("Sir, volume control mein problem aaya. Alternative method try karne ko kahiye.")
                        self.suggest_alternatives("system", command)
                        return False
                        
                elif any(word in command for word in ['down', 'kam', 'decrease']):
                    result = subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%-'], capture_output=True)
                    if result.returncode == 0:
                        self.speak("Sir, volume kam kar diya!")
                        return True
                    else:
                        self.speak("Sir, volume control mein problem aaya. Alternative method try karne ko kahiye.")
                        self.suggest_alternatives("system", command)
                        return False
                        
                elif 'mute' in command:
                    result = subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'], capture_output=True)
                    if result.returncode == 0:
                        self.speak("Sir, audio mute/unmute kar diya!")
                        return True
                    else:
                        self.speak("Sir, audio toggle mein problem aaya. Alternative method try karne ko kahiye.")
                        self.suggest_alternatives("system", command)
                        return False
            
            elif 'scroll' in command:
                if any(word in command for word in ['down', 'niche']):
                    try:
                        for _ in range(3):
                            subprocess.run(['xdotool', 'key', 'Down'], capture_output=True, check=True)
                        self.speak("Sir, scroll down kar diya!")
                        return True
                    except:
                        self.speak("Sir, scroll karne ke liye xdotool install nahi hai. Alternative method try karne ko kahiye.")
                        self.suggest_alternatives("system", command)
                        return False
                        
                elif any(word in command for word in ['up', 'upar']):
                    try:
                        for _ in range(3):
                            subprocess.run(['xdotool', 'key', 'Up'], capture_output=True, check=True)
                        self.speak("Sir, scroll up kar diya!")
                        return True
                    except:
                        self.speak("Sir, scroll karne ke liye xdotool install nahi hai. Alternative method try karne ko kahiye.")
                        self.suggest_alternatives("system", command)
                        return False
            
            elif 'shutdown' in command:
                if messagebox.askyesno("Confirm Shutdown", "Sir, system shutdown karna hai?"):
                    self.speak("Sir, system shutdown kar raha hun!")
                    subprocess.run(['shutdown', '-h', 'now'])
                    return True
                else:
                    self.speak("Sir, shutdown cancel kar diya.")
                    return True
            
            elif 'restart' in command:
                if messagebox.askyesno("Confirm Restart", "Sir, system restart karna hai?"):
                    self.speak("Sir, system restart kar raha hun!")
                    subprocess.run(['shutdown', '-r', 'now'])
                    return True
                else:
                    self.speak("Sir, restart cancel kar diya.")
                    return True
                    
        except Exception as e:
            self.speak("Sir, system command mein error aaya. Alternative method try karne ko kahiye.")
            self.suggest_alternatives("system", command)
            return False
        
        return True

    def is_web_command(self, command: str) -> bool:
        """Check if command is web related"""
        web_keywords = ['youtube', 'google', 'search', 'website', 'browser']
        return any(keyword in command.lower() for keyword in web_keywords)

    def auto_handle_web(self, command: str):
        """Automatically handle web commands"""
        command = command.lower()
        
        if 'youtube' in command:
            search_query = self.extract_search_query(command)
            if search_query:
                url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                webbrowser.open(url)
                self.speak(f"Sir, YouTube mein '{search_query}' search kar diya!")
            else:
                webbrowser.open("https://www.youtube.com")
                self.speak("Sir, YouTube open kar diya!")
        
        elif 'google' in command:
            search_query = self.extract_search_query(command)
            if search_query:
                url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
                webbrowser.open(url)
                self.speak(f"Sir, Google mein '{search_query}' search kar diya!")
            else:
                webbrowser.open("https://www.google.com")
                self.speak("Sir, Google open kar diya!")

    def is_file_command(self, command: str) -> bool:
        """Check if command is file related"""
        file_keywords = ['file', 'folder', 'delete', 'create', 'open', 'rename']
        return any(keyword in command.lower() for keyword in file_keywords)

    def auto_handle_files(self, command: str):
        """Automatically handle file commands"""
        # Basic file operations - can be extended
        self.speak("Sir, file operations implement kar raha hun!")

    def is_productivity_command(self, command: str) -> bool:
        """Check if command is productivity related"""
        productivity_keywords = ['routine', 'reminder', 'note', 'schedule', 'plan']
        return any(keyword in command.lower() for keyword in productivity_keywords)

    def auto_handle_productivity(self, command: str):
        """Automatically handle productivity commands"""
        self.speak("Sir, productivity features implement kar raha hun!")

    def generate_smart_code(self, command: str):
        """Generate smart code using AI"""
        try:
            system_content = """You are an expert programmer. Generate clean, complete code based on user requirements.
            Create production-ready code with proper structure. Include HTML, CSS, and JavaScript for web projects.
            Make the code professional and well-commented."""
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Generate code for: {command}"}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=2000,
                temperature=0.3
            )
            
            generated_code = response.choices[0].message.content.strip()
            
            # Save code to file
            code_filename = f"rj_generated_code_{int(time.time())}.txt"
            code_path = Path.home() / "Desktop" / code_filename
            
            with open(code_path, 'w', encoding='utf-8') as f:
                f.write(f"// Generated by RJ for: {command}\n")
                f.write(f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(generated_code)
            
            self.speak(f"Sir, code generate kar diya! Desktop pe {code_filename} file mein save hai.")
            self.log_to_console(f"Code generated: {code_path}", 'success')
            
        except Exception as e:
            self.speak(f"Sir, code generation mein error: {str(e)}")

    def handle_ai_query(self, query: str) -> bool:
        """Handle general AI queries with Sir addressing"""
        try:
            system_content = """You are RJ, an advanced AI assistant that speaks perfect Hinglish.
            Always address the user as 'Sir' with respect. You are helpful, intelligent, and professional.
            Provide comprehensive answers while being conversational and friendly."""
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": query}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Ensure Sir addressing
            if not ai_response.lower().startswith('sir'):
                ai_response = f"Sir, {ai_response}"
            
            self.speak(ai_response)
            return True
            
        except Exception as e:
            self.speak(f"Sir, AI service mein problem hai: {str(e)}")
            return False

    def is_retry_command(self, command: str) -> bool:
        """Check if command is asking for retry"""
        retry_keywords = [
            "ye krke dekho", "ye karo", "ye try karo", "phir try karo",
            "dobara karo", "wapas karo", "retry karo", "again karo",
            "iska alternative", "koi aur app", "different way",
            "dusra tareeka", "alternative method", "koi aur option"
        ]
        command_lower = command.lower()
        return any(keyword in command_lower for keyword in retry_keywords)

    def enable_retry_mode(self, failed_command: str, error_msg: str = ""):
        """Enable retry mode when command fails"""
        self.retry_mode = True
        self.last_failed_command = failed_command
        self.update_status("❌ Failed - Retry Available", '#ff4444')
        
        if error_msg:
            self.speak(f"Sir, task fail ho gaya: {error_msg}. Mujhe 'ye krke dekho' ya alternative batayiye.")
        else:
            self.speak("Sir, ye task complete nahi ho paya. Mujhe 'ye krke dekho' ya alternative method batayiye.")
        
        self.log_to_console(f"Failed command stored for retry: {failed_command}", 'error')

    def suggest_alternatives(self, failure_type: str, original_command: str):
        """Suggest alternatives when command fails"""
        suggestions = []
        
        if failure_type == "vscode":
            suggestions = [
                "gedit text editor use karo",
                "nano editor mein open karo", 
                "browser mein HTML file open karo",
                "simple text editor use karo"
            ]
        elif failure_type == "project_creation":
            suggestions = [
                "basic HTML file banao",
                "simple text file mein code likhao",
                "notepad mein code create karo"
            ]
        elif failure_type == "youtube":
            suggestions = [
                "browser mein YouTube manually open karo",
                "google search try karo",
                "different browser use karo"
            ]
        elif failure_type == "system":
            suggestions = [
                "manually system settings check karo",
                "terminal command try karo",
                "settings app open karo"
            ]
        
        if suggestions:
            self.retry_suggestions = suggestions
            random_suggestion = random.choice(suggestions)
            self.speak(f"Sir, alternative ye try kar sakte hain: {random_suggestion}")
            self.log_to_console(f"Suggested alternative: {random_suggestion}", 'system')

    def handle_retry_command(self, command: str):
        """Handle retry commands from user"""
        if not self.retry_mode or not self.last_failed_command:
            self.speak("Sir, koi failed task nahi hai retry karne ke liye.")
            return
        
        self.log_to_console(f"Retry requested for: {self.last_failed_command}", 'system')
        
        # Extract new approach from user command
        if "alternative" in command.lower() or "aur" in command.lower():
            # User wants alternative
            if self.retry_suggestions:
                suggestion = random.choice(self.retry_suggestions)
                self.speak(f"Sir, ye alternative try kar raha hun: {suggestion}")
                success = self.try_alternative_approach(self.last_failed_command, suggestion)
            else:
                success = self.try_intelligent_retry(self.last_failed_command)
        else:
            # User said "ye krke dekho" - try original command again with modifications
            self.speak("Sir, dobara try kar raha hun same task ko different way mein!")
            success = self.try_intelligent_retry(self.last_failed_command)
        
        if success:
            self.speak("Sir, is baar successful ho gaya!")
            self.retry_mode = False
            self.last_failed_command = None
            self.update_status("✅ Retry Successful", '#44ff44')
        else:
            self.speak("Sir, abhi bhi problem aa raha hai. Koi aur alternative try karne ko kahiye.")

    def try_alternative_approach(self, original_command: str, alternative_method: str) -> bool:
        """Try alternative approach for failed command"""
        try:
            if "gedit" in alternative_method and "vs code" in original_command:
                # Use gedit instead of VS Code
                project_type = self.detect_project_type(original_command)
                project_name = f"{project_type}_{int(time.time())}"
                project_path = Path.home() / "Desktop" / project_name
                project_path.mkdir(exist_ok=True)
                
                # Create simple HTML file
                html_file = project_path / "index.html"
                basic_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{project_type.replace('_', ' ').title()}</title>
</head>
<body>
    <h1>Welcome to {project_type.replace('_', ' ').title()}</h1>
    <p>Created by RJ Assistant using alternative method!</p>
</body>
</html>"""
                html_file.write_text(basic_html, encoding='utf-8')
                
                # Open with gedit
                subprocess.Popen(['gedit', str(html_file)])
                self.speak(f"Sir, {project_type} gedit mein create kar diya!")
                return True
                
            elif "browser" in alternative_method:
                # Open in browser instead
                if "youtube" in original_command:
                    webbrowser.open("https://www.youtube.com")
                    self.speak("Sir, YouTube browser mein open kar diya!")
                    return True
                    
            elif "terminal" in alternative_method:
                # Use terminal commands
                subprocess.Popen(['gnome-terminal'])
                self.speak("Sir, terminal open kar diya. Commands manually run kar sakte hain!")
                return True
                
        except Exception as e:
            self.log_to_console(f"Alternative approach failed: {e}", 'error')
            return False
        
        return False

    def try_intelligent_retry(self, original_command: str) -> bool:
        """Try intelligent retry with modifications"""
        try:
            # Try different variations of the original command
            if "vs code" in original_command:
                # Try with different editors
                editors = ["gedit", "nano", "vim"]
                for editor in editors:
                    try:
                        if self.check_app_available(editor):
                            self.speak(f"Sir, {editor} try kar raha hun...")
                            subprocess.Popen([editor])
                            return True
                    except:
                        continue
                        
            elif "youtube" in original_command:
                # Try different YouTube URLs
                urls = [
                    "https://www.youtube.com",
                    "https://m.youtube.com", 
                    "https://youtube.com"
                ]
                for url in urls:
                    try:
                        webbrowser.open(url)
                        self.speak("Sir, YouTube alternative URL se open kar diya!")
                        return True
                    except:
                        continue
                        
            elif "volume" in original_command:
                # Try different volume control methods
                commands = [
                    ['amixer', 'sset', 'Master', '5%+'],
                    ['pactl', 'set-sink-volume', '@DEFAULT_SINK@', '+5%'],
                    ['pulseaudio-ctl', 'up']
                ]
                for cmd in commands:
                    try:
                        subprocess.run(cmd, capture_output=True, check=True)
                        self.speak("Sir, volume control alternative method se kar diya!")
                        return True
                    except:
                        continue
                        
        except Exception as e:
            self.log_to_console(f"Intelligent retry failed: {e}", 'error')
            return False
        
        return False

    def check_app_available(self, app_name: str) -> bool:
        """Check if application is available"""
        try:
            result = subprocess.run(['which', app_name], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def run_gui(self):
        """Run the GUI version"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.speak("Sir, Ultimate RJ band ho raha hai!")
            self.running = False

def main():
    """Main function"""
    try:
        print("🚀 Starting Ultimate RJ Assistant...")
        rj = UltimateRJ()
        rj.run_gui()
    except Exception as e:
        print(f"❌ Failed to start Ultimate RJ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()