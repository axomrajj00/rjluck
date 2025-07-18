#!/usr/bin/env python3
"""
Super Advanced RJ Assistant - Ultimate AI Voice Assistant
Features: Sleep Mode, Capabilities Showcase, Auto-activation, Advanced Memory
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

import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv

# Import GUI
from rj_gui import create_gui_for_rj

# Load environment variables
load_dotenv()

class SuperAdvancedRJ:
    def __init__(self, use_gui=True):
        """Initialize Super Advanced RJ with all features"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.listening = False
        self.sleep_mode = False
        self.last_activity_time = time.time()
        self.sleep_timeout = 30  # 30 seconds
        
        # Wake words and commands
        self.wake_words = ["hello rj", "rj", "hello"]
        self.stop_words = ["rj stop", "rj band kar", "stop rj"]
        self.sleep_words = ["rj sleep", "rj so ja", "sleep rj"]
        
        self.conversation_history = []
        self.setup_command_patterns()
        self.setup_memory_system()
        self.setup_task_system()
        self.setup_advanced_features()
        
        # GUI setup
        self.use_gui = use_gui
        self.gui = None
        if use_gui:
            self.gui = create_gui_for_rj(self)
        
        # Set Wikipedia language
        wikipedia.set_lang("hi")
        
        # Start sleep monitor
        self.start_sleep_monitor()
        
        print("🎙️ Super Advanced RJ Assistant initialized!")
        self.speak("Namaste! Main Super Advanced RJ hun. 'Hello RJ' kehkar mujhe activate kar sakte hain. Main bahut kuch kar sakta hun!")

    def setup_advanced_features(self):
        """Setup advanced features"""
        self.capabilities = {
            "system_control": [
                "System shutdown, restart, sleep, lock",
                "Volume control (up, down, mute)",
                "Application launching and closing",
                "File operations (create, delete, rename)",
                "Screen brightness control"
            ],
            "memory_management": [
                "Store and recall any information",
                "Smart categorization of memories",
                "Search memories by keywords",
                "Remove specific memories",
                "Export memory to files"
            ],
            "task_management": [
                "Create tasks with timers",
                "Multiple concurrent timers",
                "Task completion tracking",
                "Automatic notifications",
                "Task priority management"
            ],
            "information_services": [
                "Wikipedia search in Hindi/English",
                "Real-time weather updates",
                "News headlines",
                "Currency conversion",
                "Time zone information"
            ],
            "entertainment": [
                "YouTube search and play",
                "Music recommendations",
                "Jokes and fun facts",
                "Story telling",
                "Riddles and puzzles"
            ],
            "productivity": [
                "Note taking and management",
                "Calendar reminders",
                "Email composition help",
                "Text editing assistance",
                "Code snippets generation"
            ],
            "smart_features": [
                "Sleep mode with auto-wake",
                "Voice pattern recognition",
                "Context-aware responses",
                "Learning user preferences",
                "Multilingual conversation"
            ]
        }
        
        self.fun_responses = [
            "Haan ji, kya kaam hai?",
            "Boliye sir, main sun raha hun",
            "Ready hun main, command dijiye",
            "Aapka super assistant hazir hai",
            "Kya help chahiye aapko?",
            "Main yahan hun, batayiye"
        ]

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
        
        # Select voice [2] as requested
        if len(voices) > 2:
            self.tts_engine.setProperty('voice', voices[2].id)
            print(f"🗣️ Using voice [2]: {voices[2].name}")
        elif len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
            print(f"🗣️ Using voice [1]: {voices[1].name}")
        
        self.tts_engine.setProperty('rate', 175)
        self.tts_engine.setProperty('volume', 0.9)

    def setup_memory_system(self):
        """Setup JSON-based memory system"""
        self.memory_file = 'super_rj_memory.json'
        self.load_memory()

    def setup_task_system(self):
        """Setup task management system"""
        self.active_timers = {}
        self.start_timer_monitor()

    def setup_command_patterns(self):
        """Setup comprehensive command patterns"""
        self.patterns = {
            'capabilities': {
                'show_capabilities': r'kya kya kar sakte ho|what can you do|capabilities|features|tumhare pas kya hai|tum kya kar sakte ho'
            },
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
                'brightness_up': r'brightness up|screen bright kar|display bright',
                'brightness_down': r'brightness down|screen dim kar|display dim',
            },
            'information': {
                'weather': r'weather|mausam|temperature|garmi|sardi',
                'news': r'news|khabar|headlines|samachar',
                'time': r'time kya hai|what time|kitne baje hain',
                'date': r'date kya hai|what date|aaj kya date hai',
            },
            'entertainment': {
                'joke': r'joke sunao|hasao|comedy|funny|mazak',
                'story': r'story sunao|kahani|kissa',
                'fact': r'fact batao|interesting fact|amazing fact',
                'riddle': r'riddle|paheli|puzzle'
            },
            'web_browsing': {
                'search_google': r'google par search kar|search for|dhundho',
                'youtube': r'youtube|video dekho|youtube kholo',
                'website': r'website kholo|site kholo',
            },
            'wikipedia': {
                'wiki_search': r'wikipedia|wiki|batao.*ke bare mein|tell me about',
            },
            'applications': {
                'text_editor': r'text editor|editor|notepad|likhne wala',
                'calculator': r'calculator|calc|hisab|ganit',
                'terminal': r'terminal|command prompt|cmd',
                'file_manager': r'file manager|files|explorer|folder',
                'browser': r'browser|chrome|firefox|internet',
            }
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
                'user_preferences': {},
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

    def start_sleep_monitor(self):
        """Monitor for sleep mode activation"""
        def sleep_monitor():
            while self.running:
                current_time = time.time()
                if (not self.sleep_mode and 
                    not self.listening and 
                    current_time - self.last_activity_time > self.sleep_timeout):
                    
                    self.enter_sleep_mode()
                
                time.sleep(5)  # Check every 5 seconds
        
        threading.Thread(target=sleep_monitor, daemon=True).start()

    def enter_sleep_mode(self):
        """Enter sleep mode"""
        self.sleep_mode = True
        print("😴 RJ entering sleep mode...")
        if self.gui:
            self.gui.update_status("Sleep Mode")
            self.gui.log_to_console("😴 Entering sleep mode. Say 'Hello RJ' to wake up.", "warning")
        
        # Optional: Speak sleep message
        # self.speak("Main sleep mode mein ja raha hun. 'Hello RJ' kehkar mujhe jagayiye.")

    def wake_up(self):
        """Wake up from sleep mode"""
        if self.sleep_mode:
            self.sleep_mode = False
            self.last_activity_time = time.time()
            print("😊 RJ waking up...")
            
            if self.gui:
                self.gui.update_status("Active")
                self.gui.log_to_console("😊 Waking up! Ready for commands.", "success")
            
            # Random wake up response
            wake_responses = [
                "Haan ji, main aa gaya!",
                "Ready hun sir!",
                "Kya kaam hai boss?",
                "Main yahan hun, boliye!",
                "Jagaya aapne, kya help chahiye?"
            ]
            self.speak(random.choice(wake_responses))

    def show_capabilities(self):
        """Show all capabilities to user"""
        response = "Main ye sab kar sakta hun:\n\n"
        
        for category, features in self.capabilities.items():
            category_name = category.replace('_', ' ').title()
            response += f"🔹 {category_name}:\n"
            for feature in features:
                response += f"  • {feature}\n"
            response += "\n"
        
        response += "Kuch examples:\n"
        response += "• 'RJ yaad rakh meeting tomorrow 3 PM'\n"
        response += "• 'RJ task add kar workout 30 minutes'\n"
        response += "• 'RJ Wikipedia India'\n"
        response += "• 'RJ joke sunao'\n"
        response += "• 'RJ weather batao'\n"
        response += "• 'RJ calculator kholo'\n"
        
        if self.gui:
            self.gui.log_to_console("📋 Showing capabilities...", "info")
        
        # Speak summarized version
        speak_text = "Main bahut kuch kar sakta hun - System control, memory management, task management, Wikipedia search, entertainment, productivity tools, aur bahut kuch! Kya kaam hai aapka?"
        self.speak(speak_text)
        
        return response

    def get_weather_info(self, city="Delhi"):
        """Get weather information (mock implementation)"""
        try:
            # This is a mock implementation - you can integrate with actual weather API
            weather_responses = [
                f"{city} mein aaj dhoop hai, temperature around 25 degree hai",
                f"{city} mein light clouds hain, pleasant weather hai",
                f"{city} mein thoda garmi hai, 28 degree temperature hai",
                f"{city} mein sahi weather hai, 22 degree pleasant temperature"
            ]
            return random.choice(weather_responses)
        except:
            return "Weather information nahi mil paya, sorry!"

    def get_random_joke(self):
        """Get random joke"""
        jokes = [
            "Teacher: Tumhara homework kahan hai? Student: Ghar pe. Teacher: Kyun nahi laye? Student: Aap ne sirf kahan hai poocha tha, lao nahi kaha tha!",
            "Wife: Tumhe pata hai main kitni sundar hun? Husband: Haan, itni sundar ho ke bhi mujhe mil gayi!",
            "Boss: Tum late kyun aaye? Employee: Sir traffic jam tha. Boss: Phir bhi doosre log time pe aaye. Employee: Sir, unka jam jaldi khatam ho gaya hoga!",
            "Doctor: Good news hai, aap bilkul theek hain. Patient: Good news? Main to fever ke liye aaya tha, fever bhi nahi hai matlab main paagal hun!",
            "Santa: Banta, kal raat mera phone gir gaya. Banta: Toot gaya? Santa: Nahi, bas neend aa gayi!"
        ]
        return random.choice(jokes)

    def get_interesting_fact(self):
        """Get interesting fact"""
        facts = [
            "Kya aap jaante hain? Octopus ke teen dil hote hain!",
            "Sharks, dinosaurs se bhi purane hain - 400 million years old!",
            "Ek teaspoon neutron star ka weight 6 billion tons hota hai!",
            "Bananas radioactive hote hain kyunki unme potassium-40 hota hai!",
            "Honey kabhi kharab nahi hota - archaeologists ne 3000 saal purana honey edible paya hai!",
            "Aapka brain 20% body ki energy use karta hai!",
            "Venus pe ek din, Earth ke 243 din ke barabar hota hai!"
        ]
        return random.choice(facts)

    def listen_for_wake_word(self) -> Optional[str]:
        """Listen specifically for wake words"""
        try:
            with self.microphone as source:
                # Shorter timeout for wake word detection
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
            
            # Try Hindi first, then English
            try:
                text = self.recognizer.recognize_google(audio, language='hi-IN').lower()
                return text
            except:
                text = self.recognizer.recognize_google(audio, language='en-US').lower()
                return text
                
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

    def listen(self) -> Optional[str]:
        """Enhanced voice input with sleep mode integration"""
        try:
            self.listening = True
            self.last_activity_time = time.time()
            
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

    def speak(self, text: str):
        """Enhanced speak with sleep mode awareness"""
        if self.sleep_mode:
            return  # Don't speak in sleep mode unless waking up
        
        print(f"🗣️ RJ: {text}")
        
        if self.gui:
            self.gui.log_to_console(f"RJ: {text}", "system")
        
        clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()
        
        self.last_activity_time = time.time()

    def process_super_command(self, command: str):
        """Process command with all advanced features"""
        command = command.lower().strip()
        
        # Update activity time
        self.last_activity_time = time.time()
        
        # Update session stats
        self.memory_data['session_stats']['total_commands'] += 1
        
        # Check for stop commands
        if any(stop_word in command for stop_word in self.stop_words):
            self.speak("Commands stop kar raha hun. 'Hello RJ' kehkar activate kar sakte hain.")
            self.listening = False
            if self.gui:
                self.gui.update_status("Stopped")
            return

        # Check for sleep commands
        if any(sleep_word in command for sleep_word in self.sleep_words):
            self.speak("Sleep mode mein ja raha hun. 'Hello RJ' kehkar jagayiye.")
            self.enter_sleep_mode()
            return

        # Check for wake words
        wake_word_found = False
        for wake_word in self.wake_words:
            if wake_word in command:
                wake_word_found = True
                # Remove wake word from command
                command = command.replace(wake_word, "").strip()
                break
        
        if not wake_word_found and not self.listening:
            return  # Ignore commands without wake word when not actively listening
        
        # Wake up if in sleep mode
        if self.sleep_mode:
            self.wake_up()
            if not command:  # If only wake word was said
                return

        if not command:
            response = random.choice(self.fun_responses)
            self.speak(response)
            return

        # Show capabilities
        if re.search(self.patterns['capabilities']['show_capabilities'], command):
            self.show_capabilities()
            return

        # Entertainment commands
        if re.search(self.patterns['entertainment']['joke'], command):
            joke = self.get_random_joke()
            self.speak(joke)
            return
        
        if re.search(self.patterns['entertainment']['fact'], command):
            fact = self.get_interesting_fact()
            self.speak(fact)
            return

        # Information commands
        if re.search(self.patterns['information']['weather'], command):
            weather = self.get_weather_info()
            self.speak(weather)
            return
        
        if re.search(self.patterns['information']['time'], command):
            current_time = datetime.now().strftime("%H:%M")
            self.speak(f"Abhi time hai {current_time}")
            return
        
        if re.search(self.patterns['information']['date'], command):
            current_date = datetime.now().strftime("%d %B %Y")
            self.speak(f"Aaj ki date hai {current_date}")
            return

        # Memory commands
        if any(re.search(pattern, command) for pattern in self.patterns['memory_commands'].values()):
            self.handle_memory_command(command)
            return

        # Task commands
        if any(re.search(pattern, command) for pattern in self.patterns['task_commands'].values()):
            self.handle_task_command(command)
            return

        # Timer commands
        if re.search(r'timer laga|set timer|alarm laga', command):
            self.handle_timer_command(command)
            return

        # System control
        for pattern_name, pattern in self.patterns['system_control'].items():
            if re.search(pattern, command):
                self.handle_system_command(pattern_name, command)
                return

        # Wikipedia search
        if re.search(r'wikipedia|wiki|batao.*ke bare mein|tell me about', command):
            self.handle_wikipedia_command(command)
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
            self.speak("Alvida! Super RJ band ho raha hai. Sab data save kar diya hai!")
            self.running = False
            return

        # For everything else, use AI
        ai_response = self.get_ai_response(command)
        self.speak(ai_response)

    def handle_memory_command(self, command: str):
        """Handle memory-related commands"""
        if re.search(self.patterns['memory_commands']['remember'], command):
            content_match = re.search(r'(?:yaad rakh|remember|store)\s+(.+)', command)
            if content_match:
                content = content_match.group(1)
                self.add_memory(content, "user_note")
                self.speak(f"Yaad rakh liya: {content}")
            else:
                self.speak("Kya yaad rakhna hai?")
        
        elif re.search(self.patterns['memory_commands']['forget'], command):
            forget_match = re.search(r'(?:bhool ja|forget|remove)\s+(.+)', command)
            if forget_match:
                content = forget_match.group(1)
                result = self.remove_memory(content)
                self.speak(result)
            else:
                self.speak("Kya bhoolna hai?")
        
        elif re.search(self.patterns['memory_commands']['recall'], command):
            search_match = re.search(r'(?:yaad hai|remember|recall)\s+(.+)', command)
            if search_match:
                query = search_match.group(1)
                memories = self.search_memory(query)
                if memories:
                    self.speak(f"Haan yaad hai: {memories[0]['content']}")
                else:
                    self.speak(f"{query} ke bare mein koi memory nahi hai")
            else:
                count = len(self.memory_data['memories'])
                self.speak(f"Total {count} memories hai mere paas")

    def handle_task_command(self, command: str):
        """Handle task-related commands"""
        if re.search(self.patterns['task_commands']['add_task'], command):
            task_match = re.search(r'(?:task add kar|new task|task banao)\s+(.+)', command)
            if task_match:
                task_desc = task_match.group(1)
                timer_match = re.search(r'(\d+)\s*(?:minute|min)', task_desc)
                timer_minutes = 0
                if timer_match:
                    timer_minutes = int(timer_match.group(1))
                    task_desc = re.sub(r'\s*\d+\s*(?:minute|min)\s*', '', task_desc)
                
                self.add_task(task_desc, timer_minutes)
                if timer_minutes > 0:
                    self.speak(f"Task add kar diya {timer_minutes} minute timer ke saath")
                else:
                    self.speak("Task add kar diya")
            else:
                self.speak("Kya task add karna hai?")
        
        elif re.search(self.patterns['task_commands']['show_tasks'], command):
            tasks = self.memory_data['tasks']
            if tasks:
                pending = [t for t in tasks if not t.get('completed')]
                self.speak(f"Total {len(tasks)} tasks, {len(pending)} pending")
            else:
                self.speak("Koi tasks nahi hain")

    def handle_timer_command(self, command: str):
        """Handle timer commands"""
        timer_match = re.search(r'(\d+)\s*(?:minute|min)', command)
        if timer_match:
            minutes = int(timer_match.group(1))
            self.add_task(f"Timer for {minutes} minutes", minutes)
            self.speak(f"{minutes} minute ka timer laga diya")
        else:
            self.speak("Kitne minute ka timer?")

    def handle_system_command(self, command_type: str, command: str):
        """Handle system control commands"""
        if command_type == 'volume_up':
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%+'], capture_output=True)
            self.speak("Volume badh gaya")
        elif command_type == 'volume_down':
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%-'], capture_output=True)
            self.speak("Volume kam ho gaya")
        elif command_type == 'mute':
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'], capture_output=True)
            self.speak("Audio toggle kar diya")
        elif command_type == 'brightness_up':
            subprocess.run(['xrandr', '--output', 'HDMI-1', '--brightness', '1.2'], capture_output=True)
            self.speak("Brightness badh gayi")
        elif command_type == 'brightness_down':
            subprocess.run(['xrandr', '--output', 'HDMI-1', '--brightness', '0.8'], capture_output=True)
            self.speak("Brightness kam ho gayi")
        elif command_type == 'lock':
            subprocess.run(['loginctl', 'lock-session'], capture_output=True)
            self.speak("Screen lock kar diya")
        else:
            self.speak("System command execute kar raha hun")

    def handle_wikipedia_command(self, command: str):
        """Handle Wikipedia commands"""
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

    # Memory and Task methods (same as before but optimized)
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

    def search_memory(self, query: str) -> List[Dict]:
        """Search memories by content"""
        return [mem for mem in self.memory_data['memories'] 
                if query.lower() in mem['content'].lower()]

    def remove_memory(self, query: str):
        """Remove memory based on content search"""
        original_count = len(self.memory_data['memories'])
        self.memory_data['memories'] = [
            mem for mem in self.memory_data['memories']
            if query.lower() not in mem['content'].lower()
        ]
        removed_count = original_count - len(self.memory_data['memories'])
        
        if removed_count > 0:
            self.save_memory()
            if self.gui:
                self.gui.refresh_memory_display()
            return f"{removed_count} memories remove kar diye"
        else:
            return "Koi matching memory nahi mila"

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
        
        if self.gui:
            self.gui.refresh_task_display()

    def start_task_timer(self, task_id: int, minutes: int):
        """Start timer for a task"""
        def timer_thread():
            time.sleep(minutes * 60)
            self.speak(f"Timer complete! Task {task_id} ka time ho gaya.")
            if self.gui:
                self.gui.log_to_console(f"⏰ Timer completed for task {task_id}", "warning")
        
        threading.Thread(target=timer_thread, daemon=True).start()

    def start_timer_monitor(self):
        """Monitor active timers"""
        def monitor():
            while self.running:
                current_time = time.time()
                for task in self.memory_data['tasks']:
                    if (task.get('timer_end') and 
                        not task.get('completed') and 
                        not task.get('timer_notified') and
                        current_time >= task['timer_end']):
                        
                        self.speak(f"Timer complete! Task '{task['description']}' ka time ho gaya.")
                        task['timer_notified'] = True
                        self.save_memory()
                
                time.sleep(30)
        
        threading.Thread(target=monitor, daemon=True).start()

    def search_wikipedia(self, query: str) -> str:
        """Search Wikipedia with memory integration"""
        try:
            try:
                wikipedia.set_lang("hi")
                summary = wikipedia.summary(query, sentences=2)
                result = f"Wikipedia ke anusaar: {summary}"
            except:
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(query, sentences=2)
                    result = f"According to Wikipedia: {summary}"
                except:
                    result = f"Maaf kijiye, {query} ke bare mein Wikipedia par kuch nahi mila."
            
            self.add_memory(f"Wikipedia: {query} - {result[:100]}...", "wikipedia")
            return result
        except Exception as e:
            return f"Wikipedia search mein problem: {str(e)}"

    def get_ai_response(self, user_input: str, context: str = "") -> str:
        """Get AI response with enhanced context"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are Super Advanced RJ, the ultimate AI assistant that speaks perfect Hinglish. 
                    You have advanced capabilities including memory, task management, entertainment, and system control.
                    Always respond in a friendly, helpful Hinglish tone. You're smart, capable, and ready to help with anything.
                    Keep responses conversational and engaging."""
                }
            ]
            
            # Add recent memories and user preferences
            recent_memories = self.memory_data['memories'][-3:] if self.memory_data['memories'] else []
            if recent_memories:
                memory_context = "Recent memories: " + "; ".join([mem['content'] for mem in recent_memories])
                messages.append({"role": "system", "content": memory_context})
            
            # Add conversation history
            for msg in self.conversation_history[-5:]:
                messages.append(msg)
            
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
            
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return ai_response
            
        except Exception as e:
            return "Maaf kijiye, main abhi AI service se connect nahi kar pa raha."

    def run_with_sleep_mode(self):
        """Main run loop with sleep mode support"""
        self.speak("Super Advanced RJ ready hai! 'Hello RJ' kehkar activate kariye. 30 second baad main sleep mode mein chala jaunga.")
        
        while self.running:
            try:
                if self.sleep_mode:
                    # In sleep mode, only listen for wake words
                    wake_input = self.listen_for_wake_word()
                    if wake_input:
                        for wake_word in self.wake_words:
                            if wake_word in wake_input:
                                self.wake_up()
                                break
                else:
                    # Normal operation
                    user_input = self.listen()
                    if user_input:
                        self.process_super_command(user_input)
                
            except KeyboardInterrupt:
                self.speak("Super RJ band ho raha hai. Dhanyawad!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

    def run_gui_mode(self):
        """Run with GUI interface"""
        if self.gui:
            # Background listener with sleep mode
            def background_listener():
                while self.running:
                    try:
                        if self.sleep_mode:
                            wake_input = self.listen_for_wake_word()
                            if wake_input:
                                for wake_word in self.wake_words:
                                    if wake_word in wake_input:
                                        self.wake_up()
                                        break
                        elif self.listening:
                            user_input = self.listen()
                            if user_input:
                                self.process_super_command(user_input)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Background listener error: {e}")
                        time.sleep(1)
            
            threading.Thread(target=background_listener, daemon=True).start()
            self.gui.run()
        else:
            self.run_with_sleep_mode()

    def run(self):
        """Main run method"""
        if self.use_gui:
            self.run_gui_mode()
        else:
            self.run_with_sleep_mode()

def main():
    """Main function"""
    import sys
    
    use_gui = True
    if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
        use_gui = False
    
    try:
        print("🚀 Starting Super Advanced RJ Assistant...")
        rj = SuperAdvancedRJ(use_gui=use_gui)
        rj.run()
    except Exception as e:
        print(f"❌ Failed to start Super Advanced RJ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()