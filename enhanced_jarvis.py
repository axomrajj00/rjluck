#!/usr/bin/env python3
"""
Enhanced JARVIS - Advanced Personal AI Assistant
Features: Advanced voice commands, GUI integration, smart file management
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import psutil
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv

# Import text editor
from text_editor import open_text_editor

# Load environment variables
load_dotenv()

class EnhancedJARVIS:
    def __init__(self):
        """Initialize Enhanced JARVIS with advanced features"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.wake_word = "jarvis"
        self.conversation_history = []
        self.setup_command_patterns()
        
        print("🤖 Enhanced JARVIS initialized successfully!")
        self.speak("Enhanced JARVIS is online and ready to assist you.")

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
            print("🎤 Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)

    def setup_command_patterns(self):
        """Setup regex patterns for command recognition"""
        self.patterns = {
            'system_control': {
                'shutdown': r'shutdown|shut down|power off',
                'restart': r'restart|reboot',
                'sleep': r'sleep|suspend',
                'lock': r'lock|lock screen',
                'volume_up': r'volume up|increase volume|louder',
                'volume_down': r'volume down|decrease volume|quieter',
                'mute': r'mute|unmute|toggle sound',
            },
            'file_operations': {
                'rename': r'rename (.*?) to (.*?)$',
                'delete': r'delete (.*?)$',
                'create': r'create (?:file|document) (.*?)$',
                'copy': r'copy (.*?) to (.*?)$',
                'move': r'move (.*?) to (.*?)$',
                'open_file': r'open (?:file|document) (.*?)$',
            },
            'applications': {
                'open_app': r'open (.*?)$',
                'close_app': r'close (.*?)$',
                'text_editor': r'text editor|editor|notepad',
                'calculator': r'calculator|calc',
                'terminal': r'terminal|command prompt|cmd',
                'file_manager': r'file manager|files|explorer',
                'browser': r'browser|chrome|firefox',
            },
            'web_browsing': {
                'search_google': r'search (?:google )?for (.*?)$',
                'open_website': r'open (?:website |site )?(.*?)$',
                'youtube': r'(?:open )?youtube|watch (.*?)$',
            },
            'text_operations': {
                'write_note': r'write (?:note|text) (.*?)$',
                'read_file': r'read (?:file|document) (.*?)$',
                'edit_file': r'edit (?:file|document) (.*?)$',
            }
        }

    def speak(self, text: str):
        """Convert text to speech with improved formatting"""
        print(f"🗣️ JARVIS: {text}")
        # Remove special characters that might cause TTS issues
        clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()

    def listen(self) -> Optional[str]:
        """Enhanced voice input with better error handling"""
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                # Adjust timeout and phrase limit based on command complexity
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=15)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio, language='en-US').lower()
            print(f"👤 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Error with speech recognition: {e}")
            return None

    def get_ai_response(self, user_input: str, context: str = "") -> str:
        """Get enhanced AI response with conversation context"""
        try:
            # Add conversation history for context
            messages = [
                {
                    "role": "system",
                    "content": """You are JARVIS, an advanced AI assistant for laptop control. 
                    You have comprehensive capabilities including system control, file management, 
                    application launching, web browsing, and intelligent conversation. 
                    Always be helpful, concise, and provide actionable responses.
                    When users ask about your capabilities, be specific about what you can do."""
                }
            ]
            
            # Add recent conversation history
            for msg in self.conversation_history[-5:]:  # Last 5 exchanges
                messages.append(msg)
            
            # Add current context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Additional context: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep only last 10 exchanges
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return ai_response
            
        except Exception as e:
            print(f"❌ Error getting AI response: {e}")
            return "I apologize, I'm experiencing some difficulty processing that request."

    # Enhanced System Control Methods
    def execute_system_command(self, command: str) -> bool:
        """Execute system commands with safety checks"""
        if 'shutdown' in command:
            self.speak("Initiating system shutdown in 10 seconds. Say 'cancel shutdown' to abort.")
            # In a real implementation, you'd want to listen for cancellation
            time.sleep(3)  # Shortened for demo
            subprocess.run(['shutdown', '-h', 'now'])
            return True
        elif 'restart' in command:
            self.speak("Restarting system in 10 seconds.")
            time.sleep(3)
            subprocess.run(['reboot'])
            return True
        elif 'sleep' in command:
            self.speak("Putting system to sleep.")
            subprocess.run(['systemctl', 'suspend'])
            return True
        elif 'lock' in command:
            self.speak("Locking the screen.")
            subprocess.run(['loginctl', 'lock-session'])
            return True
        return False

    def control_volume(self, action: str):
        """Enhanced volume control"""
        if 'up' in action or 'increase' in action or 'louder' in action:
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%+'])
            self.speak("Volume increased.")
        elif 'down' in action or 'decrease' in action or 'quieter' in action:
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%-'])
            self.speak("Volume decreased.")
        elif 'mute' in action or 'toggle' in action:
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'])
            self.speak("Audio toggled.")

    # Enhanced File Operations
    def smart_file_operation(self, operation: str, command: str) -> bool:
        """Smart file operations with pattern matching"""
        try:
            if operation == 'rename':
                match = re.search(self.patterns['file_operations']['rename'], command)
                if match:
                    old_name, new_name = match.groups()
                    old_path = Path(old_name.strip())
                    new_path = Path(new_name.strip())
                    
                    if old_path.exists():
                        old_path.rename(new_path)
                        self.speak(f"Successfully renamed {old_name} to {new_name}")
                        return True
                    else:
                        self.speak(f"File {old_name} not found")
                        return False
                        
            elif operation == 'delete':
                match = re.search(self.patterns['file_operations']['delete'], command)
                if match:
                    filename = match.group(1).strip()
                    file_path = Path(filename)
                    
                    if file_path.exists():
                        self.speak(f"Are you sure you want to delete {filename}? This action cannot be undone.")
                        # In real implementation, wait for confirmation
                        file_path.unlink()
                        self.speak(f"File {filename} has been deleted")
                        return True
                    else:
                        self.speak(f"File {filename} not found")
                        return False
                        
            elif operation == 'create':
                match = re.search(self.patterns['file_operations']['create'], command)
                if match:
                    filename = match.group(1).strip()
                    with open(filename, 'w') as f:
                        f.write("")
                    self.speak(f"Created new file: {filename}")
                    return True
                    
        except Exception as e:
            self.speak(f"Error performing file operation: {str(e)}")
            return False
        
        return False

    # Enhanced Application Control
    def launch_application(self, app_name: str):
        """Enhanced application launching with smart name resolution"""
        app_name = app_name.lower().strip()
        
        # Application mapping
        app_map = {
            'text editor': 'text_editor',
            'editor': 'text_editor',
            'notepad': 'text_editor',
            'calculator': 'gnome-calculator',
            'calc': 'gnome-calculator',
            'terminal': 'gnome-terminal',
            'command prompt': 'gnome-terminal',
            'cmd': 'gnome-terminal',
            'file manager': 'nautilus',
            'files': 'nautilus',
            'explorer': 'nautilus',
            'browser': 'firefox',
            'chrome': 'google-chrome',
            'firefox': 'firefox',
            'vscode': 'code',
            'code': 'code',
            'libreoffice': 'libreoffice',
            'writer': 'libreoffice --writer',
        }
        
        try:
            if app_name in app_map:
                if app_name in ['text editor', 'editor', 'notepad']:
                    self.speak("Opening JARVIS text editor")
                    threading.Thread(target=open_text_editor, daemon=True).start()
                else:
                    cmd = app_map[app_name].split()
                    subprocess.Popen(cmd)
                    self.speak(f"Opening {app_name}")
            else:
                # Try to open as direct command
                subprocess.Popen([app_name])
                self.speak(f"Attempting to open {app_name}")
                
        except Exception as e:
            self.speak(f"Could not open {app_name}. {str(e)}")

    def close_application(self, app_name: str):
        """Close application by name"""
        try:
            subprocess.run(['pkill', '-f', app_name])
            self.speak(f"Closed {app_name}")
        except Exception as e:
            self.speak(f"Could not close {app_name}: {str(e)}")

    # Enhanced Web Browsing
    def smart_web_browsing(self, command: str):
        """Smart web browsing with search capabilities"""
        if 'search' in command and 'google' in command:
            match = re.search(self.patterns['web_browsing']['search_google'], command)
            if match:
                query = match.group(1).strip()
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                self.speak(f"Searching Google for {query}")
                return
                
        elif 'youtube' in command:
            if 'watch' in command:
                match = re.search(r'watch (.*?)$', command)
                if match:
                    query = match.group(1).strip()
                    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    self.speak(f"Searching YouTube for {query}")
                    return
            webbrowser.open("https://www.youtube.com")
            self.speak("Opening YouTube")
            return
            
        elif 'website' in command or 'site' in command:
            match = re.search(self.patterns['web_browsing']['open_website'], command)
            if match:
                site = match.group(1).strip()
                if not site.startswith('http'):
                    site = f"https://www.{site}"
                webbrowser.open(site)
                self.speak(f"Opening {site}")
                return
                
        # Default to Google
        webbrowser.open("https://www.google.com")
        self.speak("Opening web browser")

    def process_enhanced_command(self, command: str):
        """Enhanced command processing with pattern matching"""
        command = command.lower().strip()
        
        # Check for wake word
        if self.wake_word not in command:
            return
        
        # Remove wake word
        command = command.replace(self.wake_word, "").strip()
        
        if not command:
            self.speak("Yes, how may I assist you?")
            return

        # System control
        for pattern_name, pattern in self.patterns['system_control'].items():
            if re.search(pattern, command):
                if 'volume' in pattern_name:
                    self.control_volume(command)
                else:
                    self.execute_system_command(command)
                return

        # File operations
        for operation, pattern in self.patterns['file_operations'].items():
            if re.search(pattern, command):
                if operation in ['rename', 'delete', 'create']:
                    self.smart_file_operation(operation, command)
                elif operation == 'open_file':
                    match = re.search(pattern, command)
                    if match:
                        filename = match.group(1).strip()
                        try:
                            subprocess.run(['xdg-open', filename])
                            self.speak(f"Opening {filename}")
                        except:
                            self.speak(f"Could not open {filename}")
                return

        # Application control
        for app_type, pattern in self.patterns['applications'].items():
            if re.search(pattern, command):
                if app_type == 'open_app':
                    match = re.search(pattern, command)
                    if match:
                        app_name = match.group(1).strip()
                        self.launch_application(app_name)
                elif app_type == 'close_app':
                    match = re.search(pattern, command)
                    if match:
                        app_name = match.group(1).strip()
                        self.close_application(app_name)
                else:
                    # Direct application commands
                    app_name = app_type.replace('_', ' ')
                    self.launch_application(app_name)
                return

        # Web browsing
        if any(re.search(pattern, command) for pattern in self.patterns['web_browsing'].values()):
            self.smart_web_browsing(command)
            return

        # Exit commands
        if any(word in command for word in ["exit", "quit", "stop", "goodbye", "shut down"]):
            self.speak("Goodbye! JARVIS is powering down.")
            self.running = False
            return

        # Text operations
        if 'write note' in command or 'take note' in command:
            match = re.search(r'(?:write note|take note) (.*?)$', command)
            if match:
                note_content = match.group(1).strip()
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"jarvis_note_{timestamp}.txt"
                with open(filename, 'w') as f:
                    f.write(f"JARVIS Note - {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{note_content}")
                self.speak(f"Note saved as {filename}")
                return

        # For everything else, use AI
        ai_response = self.get_ai_response(command)
        self.speak(ai_response)

    def run(self):
        """Enhanced main loop with better error handling"""
        self.speak("Enhanced JARVIS is active and ready for commands. Say 'Jarvis' followed by your request.")
        
        consecutive_errors = 0
        max_errors = 5
        
        while self.running:
            try:
                user_input = self.listen()
                if user_input:
                    self.process_enhanced_command(user_input)
                    consecutive_errors = 0  # Reset error counter on successful input
                
            except KeyboardInterrupt:
                self.speak("JARVIS is shutting down. Goodbye!")
                break
            except Exception as e:
                consecutive_errors += 1
                print(f"❌ Error in main loop: {e}")
                
                if consecutive_errors >= max_errors:
                    self.speak("I'm experiencing technical difficulties. Restarting my systems.")
                    consecutive_errors = 0
                    time.sleep(2)
                
                continue

def main():
    """Main function to start Enhanced JARVIS"""
    try:
        print("🚀 Starting Enhanced JARVIS...")
        jarvis = EnhancedJARVIS()
        jarvis.run()
    except Exception as e:
        print(f"❌ Failed to start Enhanced JARVIS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()