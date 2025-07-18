#!/usr/bin/env python3
"""
Advanced RJ Assistant - Full Featured AI Assistant
Features: JSON Memory, Task Management, Timers, GUI Interface, Advanced Commands
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
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv

# Import GUI
from rj_gui import create_gui_for_rj

# Load environment variables
load_dotenv()

class AdvancedRJAssistant:
    def __init__(self, use_gui=True):
        """Initialize Advanced RJ Assistant with all features"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.listening = False
        self.wake_word = "rj"
        self.conversation_history = []
        self.setup_command_patterns()
        self.setup_memory_system()
        self.setup_task_system()
        
        # GUI setup
        self.use_gui = use_gui
        self.gui = None
        if use_gui:
            self.gui = create_gui_for_rj(self)
        
        # Set Wikipedia language
        wikipedia.set_lang("hi")
        
        print("🎙️ Advanced RJ Assistant initialized successfully!")
        self.speak("Namaste! Main Advanced RJ hun. Main yaad rakh sakta hun, tasks manage kar sakta hun, aur GUI mein sabkuch show kar sakta hun.")

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
            print("🎤 Microphone calibrate kar raha hun...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        
        # Get available voices
        voices = self.tts_engine.getProperty('voices')
        
        # Select voice [2] as requested, or best available
        if len(voices) > 2:
            self.tts_engine.setProperty('voice', voices[2].id)
            print(f"🗣️ Using voice [2]: {voices[2].name}")
        elif len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
            print(f"🗣️ Using voice [1]: {voices[1].name}")
        
        self.tts_engine.setProperty('rate', 170)
        self.tts_engine.setProperty('volume', 0.9)

    def setup_memory_system(self):
        """Setup JSON-based memory system"""
        self.memory_file = 'rj_memory.json'
        self.load_memory()

    def setup_task_system(self):
        """Setup task management system"""
        self.active_timers = {}
        self.start_timer_monitor()

    def load_memory(self):
        """Load memory from JSON file"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memory_data = json.load(f)
        except FileNotFoundError:
            self.memory_data = {
                'memories': [],
                'tasks': [],
                'settings': {},
                'created': datetime.now().isoformat()
            }
            self.save_memory()

    def save_memory(self):
        """Save memory to JSON file"""
        self.memory_data['last_updated'] = datetime.now().isoformat()
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_data, f, ensure_ascii=False, indent=2)

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
        
        if self.gui:
            self.gui.refresh_memory_display()
            self.gui.log_to_console(f"🧠 Memory stored: {content[:50]}...", "success")

    def remove_memory(self, query: str):
        """Remove memory based on content search"""
        removed_count = 0
        original_count = len(self.memory_data['memories'])
        
        # Filter out memories containing the query
        self.memory_data['memories'] = [
            mem for mem in self.memory_data['memories']
            if query.lower() not in mem['content'].lower()
        ]
        
        removed_count = original_count - len(self.memory_data['memories'])
        
        if removed_count > 0:
            self.save_memory()
            if self.gui:
                self.gui.refresh_memory_display()
                self.gui.log_to_console(f"🗑️ Removed {removed_count} memories", "warning")
            return f"{removed_count} memories remove kar diye"
        else:
            return "Koi matching memory nahi mila"

    def search_memory(self, query: str) -> List[Dict]:
        """Search memories by content"""
        matching_memories = [
            mem for mem in self.memory_data['memories']
            if query.lower() in mem['content'].lower()
        ]
        return matching_memories

    def add_task(self, description: str, timer_minutes: int = 0):
        """Add task with optional timer"""
        task_entry = {
            'id': len(self.memory_data['tasks']) + 1,
            'description': description,
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'timer_minutes': timer_minutes,
            'timer_end': time.time() + (timer_minutes * 60) if timer_minutes > 0 else None
        }
        
        self.memory_data['tasks'].append(task_entry)
        self.save_memory()
        
        if timer_minutes > 0:
            self.start_task_timer(task_entry['id'], timer_minutes)
            timer_info = f" with {timer_minutes} minute timer"
        else:
            timer_info = ""
        
        if self.gui:
            self.gui.refresh_task_display()
            self.gui.log_to_console(f"📋 Task added: {description[:40]}...{timer_info}", "success")
        
        return f"Task add kar diya{timer_info}"

    def complete_task(self, task_index: int):
        """Mark task as completed"""
        if 0 <= task_index < len(self.memory_data['tasks']):
            self.memory_data['tasks'][task_index]['completed'] = True
            self.memory_data['tasks'][task_index]['completed_at'] = datetime.now().isoformat()
            self.save_memory()
            
            if self.gui:
                self.gui.refresh_task_display()
            
            return "Task complete kar diya"
        return "Task nahi mila"

    def remove_task(self, task_index: int):
        """Remove task by index"""
        if 0 <= task_index < len(self.memory_data['tasks']):
            removed_task = self.memory_data['tasks'].pop(task_index)
            self.save_memory()
            
            if self.gui:
                self.gui.refresh_task_display()
            
            return f"Task '{removed_task['description']}' remove kar diya"
        return "Task nahi mila"

    def start_task_timer(self, task_id: int, minutes: int):
        """Start timer for a task"""
        def timer_thread():
            time.sleep(minutes * 60)
            self.speak(f"Timer complete! Task {task_id} ka time ho gaya.")
            if self.gui:
                self.gui.log_to_console(f"⏰ Timer completed for task {task_id}", "warning")
        
        timer_thread_obj = threading.Thread(target=timer_thread, daemon=True)
        timer_thread_obj.start()
        self.active_timers[task_id] = timer_thread_obj

    def start_timer_monitor(self):
        """Monitor active timers"""
        def monitor():
            while self.running:
                current_time = time.time()
                for task in self.memory_data['tasks']:
                    if (task.get('timer_end') and 
                        not task.get('completed') and 
                        current_time >= task['timer_end']):
                        
                        self.speak(f"Timer complete! Task '{task['description']}' ka time ho gaya.")
                        if self.gui:
                            self.gui.log_to_console(f"⏰ Timer completed: {task['description']}", "warning")
                        
                        # Mark timer as notified
                        task['timer_notified'] = True
                        self.save_memory()
                
                time.sleep(30)  # Check every 30 seconds
        
        threading.Thread(target=monitor, daemon=True).start()

    def clear_all_memories(self):
        """Clear all memories"""
        self.memory_data['memories'] = []
        self.save_memory()
        
        if self.gui:
            self.gui.refresh_memory_display()

    def setup_command_patterns(self):
        """Setup regex patterns for command recognition"""
        self.patterns = {
            'memory_commands': {
                'remember': r'yaad rakh|remember|store|save memory',
                'forget': r'bhool ja|forget|remove memory|delete memory',
                'recall': r'yaad hai|remember|recall|batao memory',
            },
            'task_commands': {
                'add_task': r'task add kar|new task|kaam add kar|task banao',
                'complete_task': r'task complete|task khatam|task done',
                'remove_task': r'task remove|task delete|task hatao',
                'show_tasks': r'tasks dikhao|show tasks|task list',
            },
            'timer_commands': {
                'set_timer': r'timer laga|set timer|alarm laga',
                'stop_timer': r'timer band kar|stop timer|timer off',
            },
            'system_control': {
                'shutdown': r'shutdown|shut down|power off|band kar|computer band kar',
                'restart': r'restart|reboot|dubara start kar',
                'sleep': r'sleep|suspend|so ja|system sleep kar',
                'lock': r'lock|lock screen|screen lock kar',
                'volume_up': r'volume up|volume badhao|awaz badhao|tez kar',
                'volume_down': r'volume down|volume kam kar|awaz kam kar|dhima kar',
                'mute': r'mute|unmute|awaz band kar|sound off|chup kar',
            },
            'applications': {
                'text_editor': r'text editor|editor|notepad|likhne wala',
                'calculator': r'calculator|calc|hisab|ganit',
                'terminal': r'terminal|command prompt|cmd',
                'file_manager': r'file manager|files|explorer|folder',
                'browser': r'browser|chrome|firefox|internet',
            },
            'web_browsing': {
                'search_google': r'google par search kar|search for|dhundho',
                'youtube': r'youtube|video dekho|youtube kholo',
                'website': r'website kholo|site kholo',
            },
            'wikipedia': {
                'wiki_search': r'wikipedia|wiki|batao.*ke bare mein|tell me about',
            },
            'questions': {
                'what_is': r'kya hai|what is',
                'who_is': r'kaun hai|who is',
                'how_to': r'kaise|how to',
                'where_is': r'kahan hai|where is',
            }
        }

    def speak(self, text: str):
        """Convert text to speech with GUI logging"""
        print(f"🗣️ RJ: {text}")
        
        if self.gui:
            self.gui.log_to_console(f"RJ: {text}", "system")
        
        clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()

    def listen(self) -> Optional[str]:
        """Enhanced voice input with GUI integration"""
        try:
            self.listening = True
            if self.gui:
                self.gui.update_status("Listening...")
            
            with self.microphone as source:
                print("🎤 Sun raha hun...")
                audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=15)
            
            print("🔄 Samajh raha hun...")
            
            # Try Hindi first, then English
            try:
                text = self.recognizer.recognize_google(audio, language='hi-IN').lower()
                print(f"👤 Aapne kaha (Hindi): {text}")
                if self.gui:
                    self.gui.log_to_console(f"User (Hindi): {text}", "info")
                return text
            except:
                text = self.recognizer.recognize_google(audio, language='en-US').lower()
                print(f"👤 You said (English): {text}")
                if self.gui:
                    self.gui.log_to_console(f"User (English): {text}", "info")
                return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("❌ Samajh nahi aaya")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        finally:
            self.listening = False
            if self.gui:
                self.gui.update_status("Ready")

    def search_wikipedia(self, query: str) -> str:
        """Search Wikipedia with memory integration"""
        try:
            print(f"🔍 Wikipedia search: {query}")
            
            # Try Hindi first
            try:
                wikipedia.set_lang("hi")
                summary = wikipedia.summary(query, sentences=2)
                result = f"Wikipedia ke anusaar: {summary}"
            except:
                # Fallback to English
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(query, sentences=2)
                    result = f"According to Wikipedia: {summary}"
                except:
                    result = f"Maaf kijiye, {query} ke bare mein Wikipedia par kuch nahi mila."
            
            # Store in memory
            self.add_memory(f"Wikipedia search: {query} - {result[:100]}...", "wikipedia")
            return result
                    
        except Exception as e:
            return f"Wikipedia search mein problem: {str(e)}"

    def get_ai_response(self, user_input: str, context: str = "") -> str:
        """Get AI response with memory context"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are Advanced RJ, a highly intelligent AI assistant that speaks Hinglish. 
                    You have memory capabilities, can manage tasks with timers, and have access to Wikipedia.
                    Always respond in a friendly Hinglish tone. You can remember things users tell you
                    and manage their tasks efficiently. Keep responses helpful and conversational."""
                }
            ]
            
            # Add recent memories as context
            recent_memories = self.memory_data['memories'][-3:] if self.memory_data['memories'] else []
            if recent_memories:
                memory_context = "Recent memories: " + "; ".join([mem['content'] for mem in recent_memories])
                messages.append({"role": "system", "content": memory_context})
            
            # Add conversation history
            for msg in self.conversation_history[-5:]:
                messages.append(msg)
            
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": user_input})
            
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
            print(f"❌ AI response error: {e}")
            return "Maaf kijiye, main abhi kuch problem face kar raha hun."

    def process_advanced_command(self, command: str):
        """Process command with advanced features"""
        command = command.lower().strip()
        
        # Check for wake word
        if self.wake_word not in command:
            return
        
        # Remove wake word
        command = command.replace(self.wake_word, "").strip()
        
        if not command:
            self.speak("Haan boliye, kya kaam hai?")
            return

        # Memory commands
        if any(re.search(pattern, command) for pattern in self.patterns['memory_commands'].values()):
            if re.search(self.patterns['memory_commands']['remember'], command):
                # Extract content to remember
                content_match = re.search(r'(?:yaad rakh|remember|store|save memory)\s+(.+)', command)
                if content_match:
                    content = content_match.group(1)
                    self.add_memory(content, "user_note")
                    self.speak(f"Yaad rakh liya: {content}")
                else:
                    self.speak("Kya yaad rakhna hai? Please specify content.")
                return
                
            elif re.search(self.patterns['memory_commands']['forget'], command):
                # Extract content to forget
                forget_match = re.search(r'(?:bhool ja|forget|remove|delete)\s+(.+)', command)
                if forget_match:
                    content = forget_match.group(1)
                    result = self.remove_memory(content)
                    self.speak(result)
                else:
                    self.speak("Kya bhoolna hai? Please specify.")
                return
                
            elif re.search(self.patterns['memory_commands']['recall'], command):
                # Search and recall memories
                search_match = re.search(r'(?:yaad hai|remember|recall|batao)\s+(.+)', command)
                if search_match:
                    query = search_match.group(1)
                    memories = self.search_memory(query)
                    if memories:
                        response = f"Haan yaad hai! {len(memories)} memories mili: "
                        for mem in memories[:3]:  # Show first 3
                            response += f"{mem['content'][:50]}...; "
                        self.speak(response)
                    else:
                        self.speak(f"{query} ke bare mein koi memory nahi hai")
                else:
                    # Show all memories
                    if self.memory_data['memories']:
                        count = len(self.memory_data['memories'])
                        self.speak(f"Total {count} memories hai mere paas")
                    else:
                        self.speak("Abhi koi memories nahi hai")
                return

        # Task commands
        if any(re.search(pattern, command) for pattern in self.patterns['task_commands'].values()):
            if re.search(self.patterns['task_commands']['add_task'], command):
                # Extract task description and timer
                task_match = re.search(r'(?:task add kar|new task|kaam add kar|task banao)\s+(.+)', command)
                if task_match:
                    task_desc = task_match.group(1)
                    
                    # Check for timer
                    timer_match = re.search(r'(\d+)\s*(?:minute|min|minutes)', task_desc)
                    timer_minutes = 0
                    if timer_match:
                        timer_minutes = int(timer_match.group(1))
                        task_desc = re.sub(r'\s*\d+\s*(?:minute|min|minutes)\s*', '', task_desc)
                    
                    result = self.add_task(task_desc, timer_minutes)
                    self.speak(result)
                else:
                    self.speak("Kya task add karna hai?")
                return
                
            elif re.search(self.patterns['task_commands']['show_tasks'], command):
                tasks = self.memory_data['tasks']
                if tasks:
                    pending_tasks = [t for t in tasks if not t.get('completed')]
                    self.speak(f"Total {len(tasks)} tasks hain, {len(pending_tasks)} pending hain")
                else:
                    self.speak("Koi tasks nahi hain")
                return

        # Timer commands
        if re.search(r'timer laga|set timer|alarm laga', command):
            timer_match = re.search(r'(\d+)\s*(?:minute|min|minutes)', command)
            if timer_match:
                minutes = int(timer_match.group(1))
                self.add_task(f"Timer for {minutes} minutes", minutes)
                self.speak(f"{minutes} minute ka timer laga diya")
            else:
                self.speak("Kitne minute ka timer lagana hai?")
            return

        # Wikipedia search
        if re.search(r'wikipedia|wiki|batao.*ke bare mein|tell me about', command):
            # Extract search query
            patterns = [
                r'wikipedia\s+(.+)',
                r'wiki\s+(.+)',
                r'batao\s+(.+?)\s+ke bare mein',
                r'tell me about\s+(.+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    query = match.group(1).strip()
                    wiki_result = self.search_wikipedia(query)
                    self.speak(wiki_result)
                    return

        # Question answering with memory integration
        for question_type, pattern in self.patterns['questions'].items():
            if re.search(pattern, command):
                # First check memory
                memories = self.search_memory(command)
                if memories:
                    self.speak(f"Mere memory mein hai: {memories[0]['content']}")
                    return
                
                # Then try Wikipedia
                topic_match = re.search(r'(?:kya hai|what is|kaun hai|who is)\s+(.+)', command)
                if topic_match:
                    topic = topic_match.group(1)
                    wiki_result = self.search_wikipedia(topic)
                    if "nahi mila" not in wiki_result:
                        self.speak(wiki_result)
                        return
                
                # Fallback to AI
                ai_response = self.get_ai_response(command)
                self.speak(ai_response)
                return

        # System control (same as before)
        for pattern_name, pattern in self.patterns['system_control'].items():
            if re.search(pattern, command):
                if 'volume' in pattern_name:
                    self.control_volume(command)
                else:
                    self.execute_system_command(command)
                return

        # Application control
        if any(word in command for word in ['open', 'kholo', 'chalu kar']):
            self.handle_application_command(command)
            return

        # Web browsing
        if any(word in command for word in ['search', 'google', 'youtube', 'website']):
            self.handle_web_command(command)
            return

        # Exit commands
        if any(word in command for word in ["exit", "quit", "stop", "goodbye", "alvida", "bye"]):
            self.speak("Alvida! Sab memories aur tasks save kar diye hain. Phir milte hain!")
            self.running = False
            return

        # Note taking (store in memory)
        if any(phrase in command for phrase in ['note likh', 'yaad rakh', 'write note']):
            note_match = re.search(r'(?:note likh|yaad rakh|write note)\s+(.+)', command)
            if note_match:
                note_content = note_match.group(1)
                self.add_memory(note_content, "voice_note")
                self.speak("Note yaad rakh liya")
                return

        # For everything else, use AI with memory context
        ai_response = self.get_ai_response(command)
        self.speak(ai_response)

    def control_volume(self, action: str):
        """Volume control with feedback"""
        if any(word in action for word in ['up', 'badhao', 'tez']):
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%+'], capture_output=True)
            self.speak("Volume badh gaya.")
        elif any(word in action for word in ['down', 'kam kar', 'dhima']):
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%-'], capture_output=True)
            self.speak("Volume kam ho gaya.")
        elif any(word in action for word in ['mute', 'band kar', 'chup']):
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'], capture_output=True)
            self.speak("Audio toggle kar diya.")

    def execute_system_command(self, command: str):
        """Execute system commands safely"""
        if any(word in command for word in ['shutdown', 'band kar']):
            self.speak("5 second mein system shutdown ho raha hai.")
            time.sleep(2)  # Shortened for safety
            # subprocess.run(['shutdown', '-h', 'now'])
            self.speak("Demo mode - shutdown command executed")
        elif any(word in command for word in ['restart', 'reboot']):
            self.speak("System restart command received")
        elif any(word in command for word in ['sleep', 'suspend']):
            self.speak("Sleep mode activated")
        elif any(word in command for word in ['lock']):
            subprocess.run(['loginctl', 'lock-session'], capture_output=True)
            self.speak("Screen lock kar diya.")

    def handle_application_command(self, command: str):
        """Handle application launching"""
        app_map = {
            'calculator': 'gnome-calculator',
            'calc': 'gnome-calculator',
            'hisab': 'gnome-calculator',
            'terminal': 'gnome-terminal',
            'cmd': 'gnome-terminal',
            'files': 'nautilus',
            'folder': 'nautilus',
            'browser': 'firefox',
            'chrome': 'google-chrome',
            'firefox': 'firefox'
        }
        
        for app_name, app_cmd in app_map.items():
            if app_name in command:
                try:
                    subprocess.Popen([app_cmd])
                    self.speak(f"{app_name} khol raha hun")
                except:
                    self.speak(f"{app_name} nahi khul paya")
                return
        
        self.speak("Kaunsa application kholna hai?")

    def handle_web_command(self, command: str):
        """Handle web browsing commands"""
        if 'youtube' in command:
            webbrowser.open("https://www.youtube.com")
            self.speak("YouTube khol raha hun")
        elif 'google' in command or 'search' in command:
            search_match = re.search(r'(?:search|dhundho|google par search kar)\s+(.+)', command)
            if search_match:
                query = search_match.group(1)
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                self.speak(f"Google par {query} search kar raha hun")
            else:
                webbrowser.open("https://www.google.com")
                self.speak("Google khol raha hun")
        else:
            webbrowser.open("https://www.google.com")
            self.speak("Browser khol raha hun")

    def start_listening(self):
        """Start continuous listening mode"""
        self.listening = True

    def stop_listening(self):
        """Stop listening mode"""
        self.listening = False

    def run_console_mode(self):
        """Run in console mode without GUI"""
        self.speak("Advanced RJ ready hai! Commands boliye.")
        
        while self.running:
            try:
                user_input = self.listen()
                if user_input:
                    self.process_advanced_command(user_input)
                
            except KeyboardInterrupt:
                self.speak("Advanced RJ band ho raha hai. Dhanyawad!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    def run_gui_mode(self):
        """Run with GUI interface"""
        if self.gui:
            # Start listening in background
            def background_listener():
                while self.running:
                    try:
                        if self.listening:
                            user_input = self.listen()
                            if user_input:
                                self.process_advanced_command(user_input)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Background listener error: {e}")
                        time.sleep(1)
            
            threading.Thread(target=background_listener, daemon=True).start()
            
            # Start GUI
            self.gui.run()
        else:
            self.run_console_mode()

    def run(self):
        """Main run method"""
        if self.use_gui:
            self.run_gui_mode()
        else:
            self.run_console_mode()

def main():
    """Main function"""
    import sys
    
    # Check command line arguments
    use_gui = True
    if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
        use_gui = False
    
    try:
        print("🚀 Starting Advanced RJ Assistant...")
        rj = AdvancedRJAssistant(use_gui=use_gui)
        rj.run()
    except Exception as e:
        print(f"❌ Failed to start Advanced RJ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()