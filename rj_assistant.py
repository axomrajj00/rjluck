#!/usr/bin/env python3
"""
RJ - Personal AI Assistant with Hindi-English Support
Features: Hinglish voice commands, Wikipedia integration, system control
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

class RJAssistant:
    def __init__(self):
        """Initialize RJ Assistant with Hindi-English support"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.wake_word = "rj"
        self.conversation_history = []
        self.setup_command_patterns()
        
        # Set Wikipedia language to Hindi and English
        wikipedia.set_lang("hi")
        
        print("🎙️ RJ Assistant initialized successfully!")
        self.speak("Namaste! Main RJ hun, aapka personal assistant. Main Hindi aur English dono mein baat kar sakta hun.")

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
        """Setup speech recognition and text-to-speech with Hindi support"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            print("🎤 Microphone calibrate kar raha hun...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # Initialize text-to-speech with better voice settings
        self.tts_engine = pyttsx3.init()
        
        # Get available voices and set a better one
        voices = self.tts_engine.getProperty('voices')
        
        # Try to find a female voice or a better quality voice
        best_voice = None
        for i, voice in enumerate(voices):
            print(f"Voice {i}: {voice.name} - {voice.id}")
            # Look for female voices or specific good quality voices
            if any(keyword in voice.name.lower() for keyword in ['female', 'hindi', 'english', 'zira', 'hazel']):
                best_voice = voice
                break
        
        # If we found a good voice, use it, otherwise use voice index 2 if available
        if best_voice:
            self.tts_engine.setProperty('voice', best_voice.id)
            print(f"🗣️ Using voice: {best_voice.name}")
        elif len(voices) > 2:
            self.tts_engine.setProperty('voice', voices[2].id)
            print(f"🗣️ Using voice: {voices[2].name}")
        elif len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
            print(f"🗣️ Using voice: {voices[1].name}")
        
        # Set voice properties
        self.tts_engine.setProperty('rate', 170)  # Slightly slower for clarity
        self.tts_engine.setProperty('volume', 0.9)

    def setup_command_patterns(self):
        """Setup regex patterns for Hindi-English command recognition"""
        self.patterns = {
            'system_control': {
                'shutdown': r'shutdown|shut down|power off|band kar|computer band kar|system off',
                'restart': r'restart|reboot|dubara start kar|restart kar',
                'sleep': r'sleep|suspend|so ja|system sleep kar',
                'lock': r'lock|lock screen|screen lock kar|computer lock kar',
                'volume_up': r'volume up|volume badhao|awaz badhao|tez kar|louder',
                'volume_down': r'volume down|volume kam kar|awaz kam kar|dhima kar|quieter',
                'mute': r'mute|unmute|awaz band kar|sound off|chup kar',
            },
            'file_operations': {
                'rename': r'rename (.*?) to (.*?)$|naam badal (.*?) ko (.*?)$',
                'delete': r'delete (.*?)$|hatao (.*?)$|delete kar (.*?)$',
                'create': r'create (?:file|document) (.*?)$|banao file (.*?)$|naya file (.*?)$',
                'copy': r'copy (.*?) to (.*?)$|copy kar (.*?) ko (.*?)$',
                'move': r'move (.*?) to (.*?)$|move kar (.*?) ko (.*?)$',
                'open_file': r'open (?:file|document) (.*?)$|kholo file (.*?)$',
            },
            'applications': {
                'open_app': r'open (.*?)$|kholo (.*?)$|chalu kar (.*?)$',
                'close_app': r'close (.*?)$|band kar (.*?)$',
                'text_editor': r'text editor|editor|notepad|likhne wala|typing|likh',
                'calculator': r'calculator|calc|hisab|ganit|calculate',
                'terminal': r'terminal|command prompt|cmd|terminal kholo',
                'file_manager': r'file manager|files|explorer|folder kholo',
                'browser': r'browser|chrome|firefox|internet|web',
            },
            'web_browsing': {
                'search_google': r'search (?:google )?for (.*?)$|google par search kar (.*?)$|dhundho (.*?)$',
                'open_website': r'open (?:website |site )?(.*?)$|website kholo (.*?)$',
                'youtube': r'(?:open )?youtube|video dekho|youtube kholo|watch (.*?)$',
            },
            'wikipedia': {
                'wiki_search': r'wikipedia (.*?)$|wiki (.*?)$|batao (.*?) ke bare mein|tell me about (.*?)$|search wikipedia (.*?)$',
            },
            'questions': {
                'what_is': r'what is (.*?)$|kya hai (.*?)$|(.*?) kya hai$',
                'who_is': r'who is (.*?)$|kaun hai (.*?)$|(.*?) kaun hai$',
                'how_to': r'how to (.*?)$|kaise (.*?)$|(.*?) kaise kare$',
                'where_is': r'where is (.*?)$|kahan hai (.*?)$|(.*?) kahan hai$',
            }
        }

    def speak(self, text: str):
        """Convert text to speech with Hinglish support"""
        print(f"🗣️ RJ: {text}")
        # Clean text for better TTS
        clean_text = re.sub(r'[^\w\s.,!?-]', '', text)
        self.tts_engine.say(clean_text)
        self.tts_engine.runAndWait()

    def listen(self) -> Optional[str]:
        """Enhanced voice input with Hindi-English support"""
        try:
            with self.microphone as source:
                print("🎤 Sun raha hun...")
                audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=15)
            
            print("🔄 Samajh raha hun...")
            # Try Hindi first, then English
            try:
                text = self.recognizer.recognize_google(audio, language='hi-IN').lower()
                print(f"👤 Aapne kaha (Hindi): {text}")
                return text
            except:
                # Fallback to English
                text = self.recognizer.recognize_google(audio, language='en-US').lower()
                print(f"👤 You said (English): {text}")
                return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("❌ Samajh nahi aaya")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition mein error: {e}")
            return None

    def search_wikipedia(self, query: str) -> str:
        """Search Wikipedia in Hindi and English"""
        try:
            print(f"🔍 Wikipedia par search kar raha hun: {query}")
            
            # Try Hindi first
            try:
                wikipedia.set_lang("hi")
                summary = wikipedia.summary(query, sentences=2)
                return f"Wikipedia ke anusaar: {summary}"
            except:
                # Fallback to English
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(query, sentences=2)
                    return f"According to Wikipedia: {summary}"
                except:
                    return f"Maaf kijiye, main {query} ke bare mein Wikipedia par kuch nahi dhoond paya."
                    
        except Exception as e:
            return f"Wikipedia search mein problem hai: {str(e)}"

    def get_ai_response(self, user_input: str, context: str = "") -> str:
        """Get AI response with Hindi-English support"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are RJ, a helpful AI assistant that speaks Hindi-English mix (Hinglish). 
                    You can help with system commands, file operations, opening applications, 
                    answering questions, and general assistance. Always respond in a friendly Hinglish tone.
                    Use Hindi words naturally mixed with English. Keep responses helpful and conversational.
                    You have access to Wikipedia for factual information."""
                }
            ]
            
            # Add recent conversation history
            for msg in self.conversation_history[-5:]:
                messages.append(msg)
            
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
            print(f"❌ AI response mein error: {e}")
            return "Maaf kijiye, main abhi kuch problem face kar raha hun. Thoda baad mein try kijiye."

    # System Control Methods (same as before but with Hindi responses)
    def execute_system_command(self, command: str) -> bool:
        """Execute system commands with Hindi feedback"""
        if any(word in command for word in ['shutdown', 'band kar', 'power off']):
            self.speak("10 second mein system shutdown ho raha hai. Cancel kehne ke liye 'cancel shutdown' boliye.")
            time.sleep(3)
            subprocess.run(['shutdown', '-h', 'now'])
            return True
        elif any(word in command for word in ['restart', 'reboot', 'dubara start']):
            self.speak("System restart ho raha hai 10 second mein.")
            time.sleep(3)
            subprocess.run(['reboot'])
            return True
        elif any(word in command for word in ['sleep', 'suspend', 'so ja']):
            self.speak("System sleep mode mein ja raha hai.")
            subprocess.run(['systemctl', 'suspend'])
            return True
        elif any(word in command for word in ['lock', 'screen lock']):
            self.speak("Screen lock kar raha hun.")
            subprocess.run(['loginctl', 'lock-session'])
            return True
        return False

    def control_volume(self, action: str):
        """Volume control with Hindi feedback"""
        if any(word in action for word in ['up', 'badhao', 'tez', 'louder']):
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%+'])
            self.speak("Volume badh gaya.")
        elif any(word in action for word in ['down', 'kam kar', 'dhima', 'quieter']):
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '10%-'])
            self.speak("Volume kam ho gaya.")
        elif any(word in action for word in ['mute', 'band kar', 'chup']):
            subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'])
            self.speak("Audio toggle kar diya.")

    def launch_application(self, app_name: str):
        """Launch application with Hindi feedback"""
        app_name = app_name.lower().strip()
        
        app_map = {
            'text editor': 'text_editor',
            'editor': 'text_editor',
            'notepad': 'text_editor',
            'likhne wala': 'text_editor',
            'calculator': 'gnome-calculator',
            'calc': 'gnome-calculator',
            'hisab': 'gnome-calculator',
            'ganit': 'gnome-calculator',
            'terminal': 'gnome-terminal',
            'command prompt': 'gnome-terminal',
            'cmd': 'gnome-terminal',
            'file manager': 'nautilus',
            'files': 'nautilus',
            'folder': 'nautilus',
            'browser': 'firefox',
            'chrome': 'google-chrome',
            'firefox': 'firefox',
            'internet': 'firefox',
            'vscode': 'code',
            'code': 'code',
        }
        
        try:
            if app_name in app_map:
                if app_name in ['text editor', 'editor', 'notepad', 'likhne wala']:
                    self.speak("RJ text editor khol raha hun")
                    threading.Thread(target=open_text_editor, daemon=True).start()
                else:
                    cmd = app_map[app_name].split()
                    subprocess.Popen(cmd)
                    self.speak(f"{app_name} khol raha hun")
            else:
                subprocess.Popen([app_name])
                self.speak(f"{app_name} kholne ki koshish kar raha hun")
                
        except Exception as e:
            self.speak(f"{app_name} nahi khul paya. Error: {str(e)}")

    def smart_web_browsing(self, command: str):
        """Web browsing with Hindi support"""
        if any(word in command for word in ['search', 'google', 'dhundho']):
            # Extract search query
            for pattern in [r'search (?:google )?for (.*?)$', r'google par search kar (.*?)$', r'dhundho (.*?)$']:
                match = re.search(pattern, command)
                if match:
                    query = match.group(1).strip()
                    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    self.speak(f"Google par {query} search kar raha hun")
                    return
                    
        elif any(word in command for word in ['youtube', 'video']):
            if 'watch' in command:
                match = re.search(r'watch (.*?)$', command)
                if match:
                    query = match.group(1).strip()
                    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                    webbrowser.open(search_url)
                    self.speak(f"YouTube par {query} dhundh raha hun")
                    return
            webbrowser.open("https://www.youtube.com")
            self.speak("YouTube khol raha hun")
            return
            
        # Default browser opening
        webbrowser.open("https://www.google.com")
        self.speak("Browser khol raha hun")

    def process_command(self, command: str):
        """Process voice command with Hindi-English support"""
        command = command.lower().strip()
        
        # Check for wake word
        if self.wake_word not in command:
            return
        
        # Remove wake word
        command = command.replace(self.wake_word, "").strip()
        
        if not command:
            self.speak("Haan boliye, kya kaam hai?")
            return

        # Wikipedia search
        for pattern in self.patterns['wikipedia'].values():
            match = re.search(pattern, command)
            if match:
                query = match.group(1).strip()
                wiki_result = self.search_wikipedia(query)
                self.speak(wiki_result)
                return

        # Question answering
        for question_type, pattern in self.patterns['questions'].items():
            match = re.search(pattern, command)
            if match:
                topic = match.group(1).strip()
                # First try Wikipedia
                wiki_result = self.search_wikipedia(topic)
                if "nahi dhoond paya" not in wiki_result and "problem hai" not in wiki_result:
                    self.speak(wiki_result)
                else:
                    # Fallback to AI
                    ai_response = self.get_ai_response(command)
                    self.speak(ai_response)
                return

        # System control
        for pattern_name, pattern in self.patterns['system_control'].items():
            if re.search(pattern, command):
                if 'volume' in pattern_name:
                    self.control_volume(command)
                else:
                    self.execute_system_command(command)
                return

        # Application control
        if any(word in command for word in ['open', 'kholo', 'chalu kar']):
            if any(word in command for word in ['browser', 'internet', 'chrome', 'firefox']):
                self.smart_web_browsing(command)
            elif any(word in command for word in ['text editor', 'editor', 'likhne wala']):
                self.launch_application('text editor')
            elif any(word in command for word in ['calculator', 'calc', 'hisab']):
                self.launch_application('calculator')
            elif any(word in command for word in ['terminal', 'cmd']):
                self.launch_application('terminal')
            elif any(word in command for word in ['file manager', 'files', 'folder']):
                self.launch_application('file manager')
            else:
                # Extract app name
                for word in ['open', 'kholo', 'chalu kar']:
                    if word in command:
                        app_name = command.replace(word, "").strip()
                        if app_name:
                            self.launch_application(app_name)
                        break
            return

        # Web search and browsing
        if any(word in command for word in ['search', 'dhundho', 'youtube', 'website']):
            self.smart_web_browsing(command)
            return

        # Exit commands
        if any(word in command for word in ["exit", "quit", "stop", "goodbye", "alvida", "bye", "band kar"]):
            self.speak("Alvida! RJ band ho raha hun. Phir milte hain!")
            self.running = False
            return

        # Note taking
        if any(phrase in command for phrase in ['write note', 'note likh', 'yaad rakh']):
            match = re.search(r'(?:write note|note likh|yaad rakh) (.*?)$', command)
            if match:
                note_content = match.group(1).strip()
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"rj_note_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"RJ Note - {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{note_content}")
                self.speak(f"Note save kar diya {filename} mein")
                return

        # For everything else, use AI
        ai_response = self.get_ai_response(command)
        self.speak(ai_response)

    def run(self):
        """Main loop for RJ Assistant"""
        self.speak("RJ ready hai! 'RJ' kehkar apna command boliye. Main Wikipedia se bhi jaankari de sakta hun.")
        
        consecutive_errors = 0
        max_errors = 5
        
        while self.running:
            try:
                user_input = self.listen()
                if user_input:
                    self.process_command(user_input)
                    consecutive_errors = 0
                
            except KeyboardInterrupt:
                self.speak("RJ band ho raha hai. Dhanyawad!")
                break
            except Exception as e:
                consecutive_errors += 1
                print(f"❌ Error: {e}")
                
                if consecutive_errors >= max_errors:
                    self.speak("Kuch technical problem aa rahi hai. System restart kar raha hun.")
                    consecutive_errors = 0
                    time.sleep(2)
                
                continue

def main():
    """Main function to start RJ Assistant"""
    try:
        print("🚀 RJ Assistant start ho raha hai...")
        rj = RJAssistant()
        rj.run()
    except Exception as e:
        print(f"❌ RJ Assistant start nahi ho paya: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()