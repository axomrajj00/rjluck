#!/usr/bin/env python3
"""
JARVIS - Personal AI Assistant for Laptop Control
Features: Voice commands, system control, file management, web browsing, and more
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import psutil
from pathlib import Path
from typing import Optional, Dict, Any

import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JARVIS:
    def __init__(self):
        """Initialize JARVIS with all necessary components"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.wake_word = "jarvis"
        
        # Command mappings
        self.system_commands = {
            'shutdown': self.shutdown_system,
            'restart': self.restart_system,
            'sleep': self.sleep_system,
            'lock': self.lock_system,
            'volume_up': self.volume_up,
            'volume_down': self.volume_down,
            'mute': self.mute_system,
        }
        
        self.file_commands = {
            'rename': self.rename_file,
            'delete': self.delete_file,
            'create': self.create_file,
            'copy': self.copy_file,
            'move': self.move_file,
        }
        
        self.app_commands = {
            'open': self.open_application,
            'close': self.close_application,
            'browser': self.open_browser,
            'calculator': self.open_calculator,
            'terminal': self.open_terminal,
            'file_manager': self.open_file_manager,
        }
        
        print("🤖 JARVIS initialized successfully!")
        self.speak("Hello! JARVIS is ready to assist you.")

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
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            print("🎤 Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.8)
        
        # Set voice to female if available
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'f' in voice.id.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break

    def speak(self, text: str):
        """Convert text to speech"""
        print(f"🗣️ JARVIS: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text"""
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio).lower()
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

    def get_ai_response(self, user_input: str) -> str:
        """Get AI response from DeepSeek"""
        try:
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """You are JARVIS, a helpful AI assistant for laptop control. 
                        You can help with system commands, file operations, opening applications, 
                        answering questions, and general assistance. Keep responses concise and helpful.
                        If the user asks about system operations, provide clear instructions."""
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Error getting AI response: {e}")
            return "I'm sorry, I'm having trouble processing that request right now."

    # System Control Methods
    def shutdown_system(self):
        """Shutdown the system"""
        self.speak("Shutting down the system in 5 seconds. Say cancel to abort.")
        time.sleep(5)
        os.system("shutdown -h now")

    def restart_system(self):
        """Restart the system"""
        self.speak("Restarting the system in 5 seconds. Say cancel to abort.")
        time.sleep(5)
        os.system("reboot")

    def sleep_system(self):
        """Put system to sleep"""
        self.speak("Putting the system to sleep.")
        os.system("systemctl suspend")

    def lock_system(self):
        """Lock the system"""
        self.speak("Locking the system.")
        os.system("loginctl lock-session")

    def volume_up(self):
        """Increase system volume"""
        os.system("amixer -D pulse sset Master 10%+")
        self.speak("Volume increased.")

    def volume_down(self):
        """Decrease system volume"""
        os.system("amixer -D pulse sset Master 10%-")
        self.speak("Volume decreased.")

    def mute_system(self):
        """Toggle mute"""
        os.system("amixer -D pulse sset Master toggle")
        self.speak("Audio toggled.")

    # File Operations
    def rename_file(self, old_name: str, new_name: str):
        """Rename a file"""
        try:
            old_path = Path(old_name)
            new_path = Path(new_name)
            if old_path.exists():
                old_path.rename(new_path)
                self.speak(f"File renamed from {old_name} to {new_name}")
            else:
                self.speak(f"File {old_name} not found")
        except Exception as e:
            self.speak(f"Error renaming file: {str(e)}")

    def delete_file(self, filename: str):
        """Delete a file"""
        try:
            file_path = Path(filename)
            if file_path.exists():
                file_path.unlink()
                self.speak(f"File {filename} deleted successfully")
            else:
                self.speak(f"File {filename} not found")
        except Exception as e:
            self.speak(f"Error deleting file: {str(e)}")

    def create_file(self, filename: str, content: str = ""):
        """Create a new file"""
        try:
            with open(filename, 'w') as f:
                f.write(content)
            self.speak(f"File {filename} created successfully")
        except Exception as e:
            self.speak(f"Error creating file: {str(e)}")

    def copy_file(self, source: str, destination: str):
        """Copy a file"""
        try:
            subprocess.run(['cp', source, destination], check=True)
            self.speak(f"File copied from {source} to {destination}")
        except Exception as e:
            self.speak(f"Error copying file: {str(e)}")

    def move_file(self, source: str, destination: str):
        """Move a file"""
        try:
            subprocess.run(['mv', source, destination], check=True)
            self.speak(f"File moved from {source} to {destination}")
        except Exception as e:
            self.speak(f"Error moving file: {str(e)}")

    # Application Control
    def open_application(self, app_name: str):
        """Open an application"""
        try:
            subprocess.Popen([app_name])
            self.speak(f"Opening {app_name}")
        except Exception as e:
            self.speak(f"Could not open {app_name}: {str(e)}")

    def close_application(self, app_name: str):
        """Close an application"""
        try:
            os.system(f"pkill -f {app_name}")
            self.speak(f"Closing {app_name}")
        except Exception as e:
            self.speak(f"Error closing {app_name}: {str(e)}")

    def open_browser(self, url: str = "https://www.google.com"):
        """Open web browser with optional URL"""
        webbrowser.open(url)
        self.speak(f"Opening browser")

    def open_calculator(self):
        """Open calculator"""
        subprocess.Popen(['gnome-calculator'])
        self.speak("Opening calculator")

    def open_terminal(self):
        """Open terminal"""
        subprocess.Popen(['gnome-terminal'])
        self.speak("Opening terminal")

    def open_file_manager(self):
        """Open file manager"""
        subprocess.Popen(['nautilus'])
        self.speak("Opening file manager")

    def process_command(self, command: str):
        """Process voice command and execute appropriate action"""
        command = command.lower().strip()
        
        # Check for wake word
        if self.wake_word not in command:
            return
        
        # Remove wake word from command
        command = command.replace(self.wake_word, "").strip()
        
        if not command:
            self.speak("Yes, how can I help you?")
            return

        # System commands
        for cmd, func in self.system_commands.items():
            if cmd in command:
                func()
                return

        # File operations
        if any(cmd in command for cmd in self.file_commands.keys()):
            if "rename" in command:
                self.speak("Please specify the old filename and new filename")
                # In a real implementation, you'd need to parse the filenames
            elif "delete" in command:
                self.speak("Please specify the filename to delete")
            elif "create" in command:
                self.speak("Please specify the filename to create")
            return

        # Application commands
        if "open" in command:
            if "browser" in command or "chrome" in command or "firefox" in command:
                self.open_browser()
            elif "calculator" in command:
                self.open_calculator()
            elif "terminal" in command:
                self.open_terminal()
            elif "file manager" in command or "files" in command:
                self.open_file_manager()
            else:
                # Extract app name
                words = command.split()
                if "open" in words:
                    idx = words.index("open")
                    if idx + 1 < len(words):
                        app_name = words[idx + 1]
                        self.open_application(app_name)
            return

        # Website opening
        if "website" in command or "site" in command:
            if "google" in command:
                self.open_browser("https://www.google.com")
            elif "youtube" in command:
                self.open_browser("https://www.youtube.com")
            elif "github" in command:
                self.open_browser("https://www.github.com")
            else:
                self.speak("Which website would you like me to open?")
            return

        # Exit commands
        if any(word in command for word in ["exit", "quit", "stop", "goodbye"]):
            self.speak("Goodbye! JARVIS is shutting down.")
            self.running = False
            return

        # For everything else, use AI
        ai_response = self.get_ai_response(command)
        self.speak(ai_response)

    def run(self):
        """Main loop for JARVIS"""
        self.speak("JARVIS is now active. Say 'Jarvis' followed by your command.")
        
        while self.running:
            try:
                user_input = self.listen()
                if user_input:
                    self.process_command(user_input)
                
            except KeyboardInterrupt:
                self.speak("JARVIS is shutting down.")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                continue

def main():
    """Main function to start JARVIS"""
    try:
        jarvis = JARVIS()
        jarvis.run()
    except Exception as e:
        print(f"❌ Failed to start JARVIS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()