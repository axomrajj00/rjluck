#!/usr/bin/env python3
"""
Text Command RJ - Smart Text-based Command Interface
Features: Hindi/English understanding, Smart question asking, Direct text commands
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
        print("- aaj 1 tarikh se 30 tarikh tak routine banao")
        print("- youtube open karo aur ye song play karo: [song name]")
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
            'routine': ['routine', 'schedule', 'plan']
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
                    'language_preference': 'hinglish'
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
        
        # Check for applications
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
        
        # Specific pattern matching
        if 'routine' in command or 'schedule' in command:
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
        
        elif any(app in command for app in ['notepad', 'calculator', 'browser', 'terminal']):
            analysis['intent'] = 'app_control'
            analysis['confidence'] += 0.3
        
        elif 'volume' in command:
            analysis['intent'] = 'system_control'
            if any(word in command for word in ['up', 'badhao', 'tez']):
                analysis['parameters'] = ['up']
            elif any(word in command for word in ['down', 'kam', 'dhima']):
                analysis['parameters'] = ['down']
            elif any(word in command for word in ['mute', 'band', 'off']):
                analysis['parameters'] = ['mute']
            analysis['confidence'] += 0.4
        
        # Set confidence based on overall analysis
        if analysis['confidence'] < 0.5:
            analysis['needs_clarification'] = True
            if not analysis['clarification_type']:
                analysis['clarification_type'] = 'general_intent'
        
        return analysis

    def ask_clarification(self, analysis: Dict[str, Any], original_command: str) -> Dict[str, Any]:
        """Ask user for clarification when needed"""
        clarification_type = analysis['clarification_type']
        
        if clarification_type == 'date_range':
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
            if intent == 'app_control':
                self.handle_app_control(target, action, parameters)
            
            elif intent == 'routine_creation':
                self.handle_routine_creation(parameters, original_command)
            
            elif intent == 'youtube_play':
                self.handle_youtube_play(parameters)
            
            elif intent == 'system_control':
                self.handle_system_control(action, parameters)
            
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

    def handle_system_control(self, action: str, parameters: List):
        """Handle system control commands"""
        if parameters:
            control_type = parameters[0]
            
            if control_type == 'up':
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%+'], capture_output=True)
                response = "Volume up!" if self.short_answer_mode else "Volume badh gaya"
                self.speak(response)
            
            elif control_type == 'down':
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%-'], capture_output=True)
                response = "Volume down!" if self.short_answer_mode else "Volume kam ho gaya"
                self.speak(response)
            
            elif control_type == 'mute':
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'], capture_output=True)
                response = "Muted!" if self.short_answer_mode else "Audio toggle kar diya"
                self.speak(response)

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
        self.speak("Text Command RJ ready hai! Type karke commands dijiye.")
        
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