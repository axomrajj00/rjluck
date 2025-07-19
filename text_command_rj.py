#!/usr/bin/env python3
"""
Text Command RJ - Smart Text-based Command Interface
Features: Hindi/English understanding, Smart question asking, Direct text commands, Advanced System Controls
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
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TextCommandRJ:
    def __init__(self):
        """Initialize Text Command RJ"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.short_answer_mode = False
        
        self.conversation_history = []
        self.setup_command_patterns()
        self.setup_memory_system()
        self.setup_task_system()
        
        # Set Wikipedia language
        wikipedia.set_lang("hi")
        
        print("🎯 Text Command RJ initialized!")
        print("Type your commands in Hindi/English mix!")
        print("Examples:")
        print("- notepad open karo")
        print("- scroll down karo / niche karo")
        print("- volume jyada karo / increase karo")
        print("- shutdown karo / restart karo")
        print("- file delete karo")
        print("- Type 'exit' to quit\n")

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
        """Setup text-to-speech for responses"""
        self.tts_engine = pyttsx3.init()
        
        # Get available voices and try to set voice [2]
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 2:
            self.tts_engine.setProperty('voice', voices[2].id)
        elif len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        
        self.tts_engine.setProperty('rate', 175)
        self.tts_engine.setProperty('volume', 0.9)

    def setup_memory_system(self):
        """Setup JSON-based memory system"""
        self.memory_file = 'text_rj_memory.json'
        self.load_memory()

    def setup_task_system(self):
        """Setup task management system"""
        self.active_timers = {}

    def setup_command_patterns(self):
        """Setup smart command patterns for analysis"""
        self.app_patterns = {
            'notepad': ['notepad', 'text editor', 'editor', 'likhne wala'],
            'calculator': ['calculator', 'calc', 'hisab', 'ganit'],
            'browser': ['browser', 'chrome', 'firefox', 'internet'],
            'youtube': ['youtube', 'video'],
            'terminal': ['terminal', 'cmd', 'command prompt'],
            'files': ['files', 'folder', 'file manager', 'explorer'],
            'music': ['music', 'gaana', 'song', 'audio']
        }
        
        self.action_patterns = {
            'open': ['open', 'kholo', 'chalu kar', 'start kar'],
            'close': ['close', 'band kar', 'stop kar'],
            'play': ['play', 'chalao', 'sunao'],
            'search': ['search', 'dhundho', 'find'],
            'create': ['create', 'banao', 'make'],
            'download': ['download', 'download kar'],
            'volume': ['volume', 'awaz'],
            'routine': ['routine', 'schedule', 'plan'],
            'scroll': ['scroll', 'scrool'], # Added scroll patterns
            'delete': ['delete', 'remove', 'hatao', 'delet'],
            'shutdown': ['shutdown', 'shut down', 'power off', 'band kar', 'computer band kar'],
            'restart': ['restart', 'reboot', 'dubara start kar', 'phir se start kar']
        }
        
        # Advanced system control patterns
        self.scroll_patterns = {
            'down': ['down', 'niche', 'neeche', 'scroll down', 'scrool down'],
            'up': ['up', 'upar', 'upor', 'scroll up', 'scrool up'],
            'left': ['left', 'baye', 'bayen'],
            'right': ['right', 'daye', 'dayen']
        }
        
        self.volume_patterns = {
            'increase': ['jyada', 'badhao', 'increase', 'tez', 'up', 'volume up'],
            'decrease': ['kam', 'dhima', 'decrease', 'down', 'volume down'],
            'mute': ['mute', 'band', 'off', 'chup']
        }

    def load_memory(self):
        """Load memory from JSON file"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memory_data = json.load(f)
        except FileNotFoundError:
            self.memory_data = {
                'memories': [],
                'tasks': [],
                'routines': [],
                'user_preferences': {
                    'short_answer_mode': False,
                    'language_preference': 'hinglish',
                    'volume_step': 10,
                    'scroll_lines': 3
                },
                'session_stats': {
                    'total_commands': 0,
                    'favorite_commands': {},
                    'last_session': datetime.now().isoformat()
                },
                'created': datetime.now().isoformat()
            }
            self.save_memory()

    def save_memory(self):
        """Save memory to JSON file"""
        self.memory_data['last_updated'] = datetime.now().isoformat()
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_data, f, ensure_ascii=False, indent=2)

    def speak(self, text: str, also_print: bool = True):
        """Speak and optionally print response"""
        if also_print:
            print(f"🗣️ RJ: {text}")
        
        clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()

    def get_user_input(self, prompt: str = "📝 You: ") -> str:
        """Get text input from user"""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return "exit"

    def get_confirmation(self, action: str, details: str = "") -> bool:
        """Get user confirmation for critical actions"""
        confirmation_msg = f"Confirm: {action}"
        if details:
            confirmation_msg += f" - {details}"
        confirmation_msg += "? (yes/no)"
        
        self.speak(confirmation_msg)
        response = self.get_user_input("⚠️  Confirm (yes/no): ").lower()
        
        return response in ['yes', 'y', 'haan', 'ha', 'han', 'okay', 'ok']

    def execute_scroll_command(self, direction: str, lines: int = None):
        """Execute scroll commands using keyboard simulation"""
        if lines is None:
            lines = self.memory_data['user_preferences']['scroll_lines']
        
        try:
            if direction == 'down':
                # Simulate Page Down or Arrow Down
                for _ in range(lines):
                    subprocess.run(['xdotool', 'key', 'Down'], capture_output=True)
                response = f"Scroll down kar diya ({lines} lines)"
                
            elif direction == 'up':
                # Simulate Page Up or Arrow Up  
                for _ in range(lines):
                    subprocess.run(['xdotool', 'key', 'Up'], capture_output=True)
                response = f"Scroll up kar diya ({lines} lines)"
                
            elif direction == 'left':
                subprocess.run(['xdotool', 'key', 'Left'], capture_output=True)
                response = "Scroll left kar diya"
                
            elif direction == 'right':
                subprocess.run(['xdotool', 'key', 'Right'], capture_output=True)
                response = "Scroll right kar diya"
            
            else:
                response = "Scroll direction samajh nahi aaya"
            
            self.speak(response)
            
        except FileNotFoundError:
            # Fallback if xdotool not available
            self.speak("Scroll feature ke liye xdotool install karna padega: sudo apt install xdotool")
        except Exception as e:
            self.speak(f"Scroll error: {str(e)}")

    def execute_volume_command(self, action: str, step: int = None):
        """Execute volume commands with feedback"""
        if step is None:
            step = self.memory_data['user_preferences']['volume_step']
        
        try:
            if action == 'increase':
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{step}%+'], capture_output=True)
                current_volume = self.get_current_volume()
                response = f"Volume {step}% badhaya. Current: {current_volume}%"
                self.speak(response)
                
                # Ask if more adjustment needed
                self.speak("Sir, itna thik hai na? Aur badhana hai?")
                more_response = self.get_user_input("🔊 More volume? (yes/no): ").lower()
                
                if more_response in ['yes', 'y', 'haan', 'aur', 'thoda aur']:
                    self.speak("Thoda aur badha raha hun")
                    subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{step//2}%+'], capture_output=True)
                    new_volume = self.get_current_volume()
                    self.speak(f"Volume aur badha diya. Now: {new_volume}%")
                
            elif action == 'decrease':
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{step}%-'], capture_output=True)
                current_volume = self.get_current_volume()
                response = f"Volume {step}% kam kiya. Current: {current_volume}%"
                self.speak(response)
                
                # Ask if more adjustment needed
                self.speak("Sir, itna thik hai na? Aur kam karna hai?")
                more_response = self.get_user_input("🔉 Less volume? (yes/no): ").lower()
                
                if more_response in ['yes', 'y', 'haan', 'aur', 'thoda aur']:
                    self.speak("Thoda aur kam kar raha hun")
                    subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{step//2}%-'], capture_output=True)
                    new_volume = self.get_current_volume()
                    self.speak(f"Volume aur kam kar diya. Now: {new_volume}%")
                
            elif action == 'mute':
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'], capture_output=True)
                self.speak("Audio mute/unmute kar diya")
            
        except Exception as e:
            self.speak(f"Volume control error: {str(e)}")

    def get_current_volume(self) -> int:
        """Get current system volume percentage"""
        try:
            result = subprocess.run(['amixer', '-D', 'pulse', 'get', 'Master'], 
                                  capture_output=True, text=True)
            # Extract volume percentage from output
            import re
            match = re.search(r'\[(\d+)%\]', result.stdout)
            if match:
                return int(match.group(1))
            return 50  # Default fallback
        except:
            return 50

    def execute_delete_command(self, target: str = None):
        """Execute delete commands with confirmation"""
        if not target:
            self.speak("Kya delete karna hai? File path ya name batayiye.")
            target = self.get_user_input("🗑️  Delete target: ")
        
        if not target:
            self.speak("Delete target nahi mila")
            return
        
        # Confirm deletion
        if self.get_confirmation("Delete", f"'{target}' file/folder"):
            try:
                target_path = Path(target)
                
                if target_path.exists():
                    if target_path.is_file():
                        target_path.unlink()
                        self.speak(f"File '{target}' delete kar diya")
                    elif target_path.is_dir():
                        import shutil
                        shutil.rmtree(target_path)
                        self.speak(f"Folder '{target}' delete kar diya")
                else:
                    self.speak(f"'{target}' file/folder exist nahi karta")
                    
            except Exception as e:
                self.speak(f"Delete error: {str(e)}")
        else:
            self.speak("Delete cancel kar diya")

    def execute_shutdown_command(self):
        """Execute shutdown with confirmation"""
        if self.get_confirmation("System Shutdown", "Computer completely band ho jayega"):
            self.speak("5 second mein shutdown ho raha hai...")
            time.sleep(2)
            self.speak("Goodbye!")
            subprocess.run(['shutdown', '-h', 'now'])
        else:
            self.speak("Shutdown cancel kar diya")

    def execute_restart_command(self):
        """Execute restart with confirmation"""
        if self.get_confirmation("System Restart", "Computer restart ho jayega"):
            self.speak("5 second mein restart ho raha hai...")
            time.sleep(2)
            self.speak("Restart kar raha hun!")
            subprocess.run(['shutdown', '-r', 'now'])
        else:
            self.speak("Restart cancel kar diya")

    def analyze_command_intent(self, command: str) -> Dict[str, Any]:
        """Analyze command to understand intent and extract information"""
        command = command.lower().strip()
        
        analysis = {
            'intent': 'general',
            'action': None,
            'target': None,
            'parameters': [],
            'needs_clarification': False,
            'clarification_type': None,
            'confidence': 0.0
        }
        
        # Check for scroll commands
        if any(word in command for word in ['scroll', 'scrool']):
            analysis['intent'] = 'scroll_control'
            analysis['confidence'] += 0.4
            
            for direction, patterns in self.scroll_patterns.items():
                if any(pattern in command for pattern in patterns):
                    analysis['parameters'] = [direction]
                    analysis['confidence'] += 0.4
                    break
            
            if not analysis['parameters']:
                analysis['needs_clarification'] = True
                analysis['clarification_type'] = 'scroll_direction'
        
        # Check for volume commands
        elif 'volume' in command or any(word in command for word in ['jyada', 'kam', 'badhao', 'increase', 'decrease']):
            analysis['intent'] = 'volume_control'
            analysis['confidence'] += 0.4
            
            for action, patterns in self.volume_patterns.items():
                if any(pattern in command for pattern in patterns):
                    analysis['parameters'] = [action]
                    analysis['confidence'] += 0.4
                    break
        
        # Check for delete commands
        elif any(word in command for word in ['delete', 'remove', 'hatao', 'delet']):
            analysis['intent'] = 'delete_operation'
            analysis['confidence'] += 0.5
            
            # Try to extract file/folder name
            delete_patterns = [
                r'delete\s+(.+)',
                r'remove\s+(.+)',
                r'hatao\s+(.+)',
                r'delet\s+(.+)'
            ]
            
            for pattern in delete_patterns:
                match = re.search(pattern, command)
                if match:
                    target = match.group(1).strip()
                    analysis['parameters'] = [target]
                    analysis['confidence'] += 0.3
                    break
        
        # Check for shutdown/restart
        elif any(word in command for word in self.action_patterns['shutdown']):
            analysis['intent'] = 'system_shutdown'
            analysis['confidence'] = 0.9
        
        elif any(word in command for word in self.action_patterns['restart']):
            analysis['intent'] = 'system_restart'
            analysis['confidence'] = 0.9
        
        # Check for applications
        elif any(app in command for app in ['notepad', 'calculator', 'browser', 'terminal']):
            for app, patterns in self.app_patterns.items():
                if any(pattern in command for pattern in patterns):
                    analysis['target'] = app
                    analysis['confidence'] += 0.3
                    break
            
            # Check for actions
            for action, patterns in self.action_patterns.items():
                if any(pattern in command for pattern in patterns):
                    analysis['action'] = action
                    analysis['confidence'] += 0.3
                    break
            
            analysis['intent'] = 'app_control'
        
        # Check for routine creation
        elif 'routine' in command or 'schedule' in command:
            analysis['intent'] = 'routine_creation'
            
            # Extract date range
            date_match = re.search(r'(\d+)\s*(?:tarikh|date)?\s*se\s*(?:leke)?\s*(\d+)\s*(?:tarikh|date)', command)
            if date_match:
                start_date = int(date_match.group(1))
                end_date = int(date_match.group(2))
                analysis['parameters'] = [start_date, end_date]
                analysis['confidence'] += 0.4
            else:
                analysis['needs_clarification'] = True
                analysis['clarification_type'] = 'date_range'
        
        # Check for YouTube
        elif 'youtube' in command and ('song' in command or 'video' in command):
            analysis['intent'] = 'youtube_play'
            
            # Extract song/video name
            song_patterns = [
                r'(?:song|video|gaana)\s+play\s+(?:karo|kar)\s*:?\s*(.+)',
                r'ye\s+(?:song|video|gaana)\s+play\s+(?:karo|kar)\s*:?\s*(.+)',
                r'play\s+(?:karo|kar)\s*:?\s*(.+)',
                r'sunao\s*:?\s*(.+)'
            ]
            
            song_name = None
            for pattern in song_patterns:
                match = re.search(pattern, command)
                if match:
                    song_name = match.group(1).strip()
                    break
            
            if song_name and len(song_name) > 2:
                analysis['parameters'] = [song_name]
                analysis['confidence'] += 0.4
            else:
                analysis['needs_clarification'] = True
                analysis['clarification_type'] = 'song_name'
        
        # Set confidence based on overall analysis
        if analysis['confidence'] < 0.5 and not analysis['needs_clarification']:
            analysis['needs_clarification'] = True
            if not analysis['clarification_type']:
                analysis['clarification_type'] = 'general_intent'
        
        return analysis

    def ask_clarification(self, analysis: Dict[str, Any], original_command: str) -> Dict[str, Any]:
        """Ask user for clarification when needed"""
        clarification_type = analysis['clarification_type']
        
        if clarification_type == 'scroll_direction':
            self.speak("Kya direction mein scroll karna hai? (up/down/left/right)")
            direction_input = self.get_user_input("⬆️⬇️ Direction: ").lower()
            
            for direction, patterns in self.scroll_patterns.items():
                if any(pattern in direction_input for pattern in patterns):
                    analysis['parameters'] = [direction]
                    analysis['needs_clarification'] = False
                    analysis['confidence'] = 0.9
                    break
        
        elif clarification_type == 'date_range':
            self.speak("Routine ke liye date range batayiye (example: 1 se 30 tarikh)")
            date_input = self.get_user_input("📅 Date range: ")
            
            date_match = re.search(r'(\d+)\s*se\s*(\d+)', date_input)
            if date_match:
                start_date = int(date_match.group(1))
                end_date = int(date_match.group(2))
                analysis['parameters'] = [start_date, end_date]
                analysis['needs_clarification'] = False
                analysis['confidence'] = 0.9
        
        elif clarification_type == 'song_name':
            self.speak("Kya song ya video play karna chahte hain? Name batayiye.")
            song_input = self.get_user_input("🎵 Song/Video name: ")
            
            if song_input and len(song_input) > 2:
                analysis['parameters'] = [song_input]
                analysis['needs_clarification'] = False
                analysis['confidence'] = 0.9
        
        elif clarification_type == 'general_intent':
            # Use AI to understand better
            ai_response = self.get_smart_clarification(original_command)
            self.speak(ai_response)
            
            clarification_input = self.get_user_input("🤔 Clarification: ")
            
            # Re-analyze with additional context
            combined_command = f"{original_command} {clarification_input}"
            analysis = self.analyze_command_intent(combined_command)
        
        return analysis

    def get_smart_clarification(self, command: str) -> str:
        """Use AI to ask smart clarification questions"""
        try:
            system_content = """You are RJ, a smart AI assistant. User gave a command but it's not clear. 
            Ask a specific clarifying question in Hinglish to understand what they want.
            Keep it short and helpful. Examples:
            - "Kya app open karna hai?"
            - "Kitne din ka routine chahiye?"
            - "Kya search karna hai?"
            
            Be specific and don't ask generic questions."""
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Command unclear: '{command}'. What specific question should I ask?"}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "Maaf kijiye, aap kya karna chahte hain? Thoda aur detail mein batayiye."

    def execute_command(self, analysis: Dict[str, Any], original_command: str):
        """Execute the analyzed command"""
        intent = analysis['intent']
        action = analysis['action']
        target = analysis['target']
        parameters = analysis['parameters']
        
        self.memory_data['session_stats']['total_commands'] += 1
        
        try:
            if intent == 'scroll_control':
                direction = parameters[0] if parameters else 'down'
                self.execute_scroll_command(direction)
            
            elif intent == 'volume_control':
                action = parameters[0] if parameters else 'increase'
                self.execute_volume_command(action)
            
            elif intent == 'delete_operation':
                target = parameters[0] if parameters else None
                self.execute_delete_command(target)
            
            elif intent == 'system_shutdown':
                self.execute_shutdown_command()
            
            elif intent == 'system_restart':
                self.execute_restart_command()
            
            elif intent == 'app_control':
                self.handle_app_control(target, action, parameters)
            
            elif intent == 'routine_creation':
                self.handle_routine_creation(parameters, original_command)
            
            elif intent == 'youtube_play':
                self.handle_youtube_play(parameters)
            
            else:
                # Use AI for general queries
                self.handle_ai_query(original_command)
                
        except Exception as e:
            self.speak(f"Error: {str(e)}")
            print(f"❌ Error executing command: {e}")

    def handle_app_control(self, target: str, action: str, parameters: List):
        """Handle application control"""
        app_commands = {
            'notepad': 'gedit',  # or 'notepad' on Windows
            'calculator': 'gnome-calculator',
            'browser': 'firefox',
            'terminal': 'gnome-terminal',
            'files': 'nautilus'
        }
        
        if target in app_commands:
            if action == 'open' or not action:
                try:
                    subprocess.Popen([app_commands[target]])
                    response = f"{target.title()} khol diya!" if not self.short_answer_mode else f"{target} opened!"
                    self.speak(response)
                except Exception as e:
                    self.speak(f"{target} nahi khul paya. Error: {str(e)}")
            else:
                self.speak(f"{target} ke liye {action} action available nahi hai.")
        else:
            self.speak(f"{target} app recognize nahi kar paya.")

    def handle_routine_creation(self, parameters: List, original_command: str):
        """Handle routine creation with AI assistance"""
        if len(parameters) >= 2:
            start_date, end_date = parameters[0], parameters[1]
            
            self.speak(f"Routine bana raha hun {start_date} tarikh se {end_date} tarikh tak...")
            
            # Extract routine type from command
            routine_context = re.sub(r'\d+\s*(?:tarikh|date)?\s*se\s*(?:leke)?\s*\d+\s*(?:tarikh|date)', '', original_command)
            routine_context = routine_context.replace('routine', '').replace('banao', '').strip()
            
            if not routine_context:
                self.speak("Kya type ka routine chahiye? (example: exercise, study, work)")
                routine_type = self.get_user_input("📋 Routine type: ")
            else:
                routine_type = routine_context
            
            # Generate routine using AI
            routine = self.generate_routine_with_ai(start_date, end_date, routine_type)
            
            # Save routine
            routine_entry = {
                'id': len(self.memory_data['routines']) + 1,
                'type': routine_type,
                'start_date': start_date,
                'end_date': end_date,
                'routine': routine,
                'created_at': datetime.now().isoformat()
            }
            
            self.memory_data['routines'].append(routine_entry)
            self.save_memory()
            
            self.speak("Routine ready hai! File mein save kar diya hai.")
            
            # Ask if user wants to see it
            self.speak("Routine dekhna chahte hain?")
            show_response = self.get_user_input("📋 Show routine? (yes/no): ")
            
            if show_response.lower() in ['yes', 'y', 'haan', 'ha']:
                print(f"\n📅 ROUTINE ({start_date} to {end_date}) - {routine_type.upper()}")
                print("=" * 50)
                print(routine)
                print("=" * 50)

    def generate_routine_with_ai(self, start_date: int, end_date: int, routine_type: str) -> str:
        """Generate routine using AI"""
        try:
            system_content = f"""You are creating a {routine_type} routine from {start_date} to {end_date} date.
            Create a practical, day-wise routine in Hinglish.
            Make it specific and actionable.
            Format: Date - Activities
            Keep it realistic and helpful."""
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Create a detailed {routine_type} routine for {end_date - start_date + 1} days starting from {start_date} date"}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Sample {routine_type} routine:\n{start_date} - Start with basics\n{start_date + 1} - Continue practice\n... (AI error: {str(e)})"

    def handle_youtube_play(self, parameters: List):
        """Handle YouTube video/song playing"""
        if parameters:
            song_name = parameters[0]
            
            # Open YouTube search
            search_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
            webbrowser.open(search_url)
            
            response = f"YouTube mein '{song_name}' search kar diya!" if not self.short_answer_mode else f"Searching '{song_name}'"
            self.speak(response)
            
            # Save to memory
            self.add_memory(f"YouTube search: {song_name}", "youtube_search")
        else:
            self.speak("Song name nahi mila. Kya search karna hai?")

    def handle_ai_query(self, query: str):
        """Handle general AI queries"""
        try:
            system_content = """You are RJ, a helpful AI assistant that speaks perfect Hinglish.
            Answer user queries helpfully and conversationally.
            Keep responses natural and engaging."""
            
            if self.short_answer_mode:
                system_content += "\n\nUser prefers SHORT answers. Be brief and concise."
            
            messages = [
                {"role": "system", "content": system_content},
                *self.conversation_history[-5:],  # Recent context
                {"role": "user", "content": query}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=200 if self.short_answer_mode else 400,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            self.speak(ai_response)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
                
        except Exception as e:
            self.speak("AI service mein problem hai. Sorry!")

    def add_memory(self, content: str, memory_type: str = "note"):
        """Add memory to JSON storage"""
        memory_entry = {
            'id': len(self.memory_data['memories']) + 1,
            'content': content,
            'type': memory_type,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': datetime.now().isoformat()
        }
        
        self.memory_data['memories'].append(memory_entry)
        self.save_memory()

    def process_text_command(self, command: str):
        """Main method to process text commands"""
        if not command or command.lower() in ['exit', 'quit', 'bye']:
            self.speak("Alvida! Text Command RJ band ho raha hai.")
            self.running = False
            return
        
        # Special commands
        if command.lower() in ['short mode', 'short answer mode']:
            self.short_answer_mode = True
            self.speak("Short answer mode ON!")
            return
        
        if command.lower() in ['normal mode', 'detailed mode']:
            self.short_answer_mode = False
            self.speak("Normal detailed mode ON!")
            return
        
        # Show thinking process
        print("🤔 Analyzing command...")
        
        # Analyze command intent
        analysis = self.analyze_command_intent(command)
        
        print(f"📊 Intent: {analysis['intent']}, Confidence: {analysis['confidence']:.1f}")
        
        # Ask for clarification if needed
        if analysis['needs_clarification']:
            print("❓ Need clarification...")
            analysis = self.ask_clarification(analysis, command)
        
        # Execute command
        if not analysis['needs_clarification']:
            print("✅ Executing command...")
            self.execute_command(analysis, command)
        else:
            self.speak("Command samajh nahi aaya. Kya karna chahte hain?")

    def run(self):
        """Main run loop for text commands"""
        self.speak("Text Command RJ ready hai! Advanced controls ke saath. Type karke commands dijiye.")
        
        while self.running:
            try:
                # Get text input from user
                user_command = self.get_user_input()
                
                if user_command:
                    print(f"\n📝 Processing: '{user_command}'")
                    self.process_text_command(user_command)
                    print("\n" + "="*60 + "\n")
                
            except KeyboardInterrupt:
                self.speak("Alvida! Text Command RJ band ho raha hai.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                self.speak("Kuch error aaya hai. Phir try kariye.")

def main():
    """Main function"""
    try:
        print("🚀 Starting Text Command RJ...")
        rj = TextCommandRJ()
        rj.run()
    except Exception as e:
        print(f"❌ Failed to start Text Command RJ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()