#!/usr/bin/env python3
"""
Advanced Coding RJ - AI-Powered Development Assistant
Features: VS Code integration, Code generation, ChatGPT access, Screen reading, Translation
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

# Additional imports for advanced features
import pyautogui
import pytesseract
from PIL import Image, ImageGrab
import cv2
import numpy as np

# Load environment variables
load_dotenv()

class AdvancedCodingRJ:
    def __init__(self):
        """Initialize Advanced Coding RJ"""
        self.setup_ai_client()
        self.setup_speech_components()
        self.running = True
        self.short_answer_mode = False
        
        self.conversation_history = []
        self.setup_command_patterns()
        self.setup_memory_system()
        self.setup_coding_environment()
        
        # Set Wikipedia language
        wikipedia.set_lang("hi")
        
        print("🎯 Advanced Coding RJ initialized!")
        print("Coding Assistant Features:")
        print("- VS Code integration with auto-detection")
        print("- AI-powered code generation")
        print("- ChatGPT access and search")
        print("- Screen reading and OCR")
        print("- Real-time translation")
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
        
        voices = self.tts_engine.getProperty('voices')
        if len(voices) > 2:
            self.tts_engine.setProperty('voice', voices[2].id)
        elif len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)
        
        self.tts_engine.setProperty('rate', 175)
        self.tts_engine.setProperty('volume', 0.9)

    def setup_memory_system(self):
        """Setup JSON-based memory system"""
        self.memory_file = 'coding_rj_memory.json'
        self.load_memory()

    def setup_coding_environment(self):
        """Setup coding environment detection"""
        self.coding_apps = {
            'vscode': {
                'commands': ['code', '/usr/bin/code', '/snap/bin/code'],
                'check_running': 'code',
                'name': 'Visual Studio Code'
            },
            'sublime': {
                'commands': ['subl', 'sublime_text'],
                'check_running': 'sublime',
                'name': 'Sublime Text'
            },
            'atom': {
                'commands': ['atom'],
                'check_running': 'atom',
                'name': 'Atom'
            },
            'vim': {
                'commands': ['vim'],
                'check_running': 'vim',
                'name': 'Vim'
            }
        }

    def setup_command_patterns(self):
        """Setup smart command patterns for coding"""
        self.coding_patterns = {
            'open_vscode': ['vs code', 'vscode', 'visual studio code', 'code editor'],
            'generate_code': ['code banao', 'coding karo', 'website banao', 'program banao', 'script likhao'],
            'chatgpt_access': ['chat gpt', 'chatgpt', 'gpt', 'openai'],
            'screen_read': ['screen padho', 'screen read', 'dekho screen', 'kya dikha raha'],
            'translate': ['translate', 'anuwad', 'convert language', 'language change']
        }
        
        self.web_project_types = {
            'login_page': ['login page', 'login form', 'signin page'],
            'dashboard': ['dashboard', 'admin panel', 'control panel'],
            'portfolio': ['portfolio', 'personal website', 'resume site'],
            'ecommerce': ['shopping site', 'ecommerce', 'online store'],
            'blog': ['blog', 'blogging site', 'article site'],
            'landing_page': ['landing page', 'promo site', 'marketing page']
        }

    def load_memory(self):
        """Load memory from JSON file"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memory_data = json.load(f)
        except FileNotFoundError:
            self.memory_data = {
                'memories': [],
                'coding_projects': [],
                'generated_code': [],
                'screen_readings': [],
                'translations': [],
                'user_preferences': {
                    'preferred_language': 'python',
                    'code_style': 'clean',
                    'framework_preference': 'react'
                },
                'session_stats': {
                    'total_commands': 0,
                    'code_generations': 0,
                    'translations': 0,
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

    def check_app_installed(self, app_name: str) -> bool:
        """Check if coding application is installed"""
        app_info = self.coding_apps.get(app_name)
        if not app_info:
            return False
        
        for command in app_info['commands']:
            try:
                result = subprocess.run(['which', command], capture_output=True, text=True)
                if result.returncode == 0:
                    return True
            except:
                continue
        return False

    def check_app_running(self, app_name: str) -> bool:
        """Check if application is currently running"""
        app_info = self.coding_apps.get(app_name)
        if not app_info:
            return False
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if app_info['check_running'].lower() in proc.info['name'].lower():
                    return True
        except:
            pass
        return False

    def open_vscode_with_project(self, project_type: str = None):
        """Open VS Code and optionally create a project"""
        # Check if VS Code is installed
        if not self.check_app_installed('vscode'):
            self.speak("VS Code install nahi hai. Pehle install karna padega.")
            self.speak("Install command: sudo snap install code --classic")
            return False
        
        # Check if already running
        if self.check_app_running('vscode'):
            self.speak("VS Code already running hai!")
        else:
            self.speak("VS Code open kar raha hun...")
            try:
                subprocess.Popen(['code'])
                time.sleep(3)  # Wait for VS Code to open
                self.speak("VS Code successfully open ho gaya!")
            except Exception as e:
                self.speak(f"VS Code open karne mein error: {str(e)}")
                return False
        
        # If project type specified, generate code
        if project_type:
            self.generate_project_code(project_type)
        
        return True

    def generate_project_code(self, project_type: str):
        """Generate code for specific project type"""
        self.speak(f"{project_type} ke liye code generate kar raha hun...")
        
        # Create project directory
        project_name = f"{project_type.replace(' ', '_')}_{int(time.time())}"
        project_path = Path.home() / "Desktop" / project_name
        project_path.mkdir(exist_ok=True)
        
        try:
            if 'login page' in project_type.lower():
                self.create_login_page(project_path)
            elif 'dashboard' in project_type.lower():
                self.create_dashboard(project_path)
            elif 'portfolio' in project_type.lower():
                self.create_portfolio(project_path)
            else:
                self.create_basic_website(project_path, project_type)
            
            # Open project in VS Code
            subprocess.Popen(['code', str(project_path)])
            
            self.speak(f"{project_type} successfully create kar diya! VS Code mein open ho gaya.")
            
            # Save to memory
            project_entry = {
                'type': project_type,
                'path': str(project_path),
                'created_at': datetime.now().isoformat()
            }
            self.memory_data['coding_projects'].append(project_entry)
            self.memory_data['session_stats']['code_generations'] += 1
            self.save_memory()
            
        except Exception as e:
            self.speak(f"Code generation mein error: {str(e)}")

    def create_login_page(self, project_path: Path):
        """Create a beautiful login page"""
        # HTML file
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Page</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <h2>Welcome Back</h2>
            <form id="loginForm">
                <div class="input-group">
                    <input type="email" id="email" required>
                    <label for="email">Email</label>
                </div>
                <div class="input-group">
                    <input type="password" id="password" required>
                    <label for="password">Password</label>
                </div>
                <button type="submit">Login</button>
                <div class="forgot-password">
                    <a href="#">Forgot Password?</a>
                </div>
            </form>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>'''
        
        # CSS file
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
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

.login-box {
    width: 300px;
}

h2 {
    color: white;
    text-align: center;
    margin-bottom: 30px;
    font-weight: 300;
}

.input-group {
    position: relative;
    margin-bottom: 25px;
}

input {
    width: 100%;
    padding: 15px 0;
    background: transparent;
    border: none;
    border-bottom: 2px solid rgba(255, 255, 255, 0.5);
    color: white;
    font-size: 16px;
    outline: none;
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
    color: #fff;
}

button {
    width: 100%;
    padding: 15px;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 25px;
    color: white;
    font-size: 16px;
    cursor: pointer;
    transition: 0.3s;
}

button:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.forgot-password {
    text-align: center;
    margin-top: 20px;
}

.forgot-password a {
    color: rgba(255, 255, 255, 0.7);
    text-decoration: none;
    font-size: 14px;
}'''
        
        # JavaScript file
        js_content = '''document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (email && password) {
        alert('Login successful! Welcome back.');
        // Here you can add actual login logic
    } else {
        alert('Please fill in all fields.');
    }
});

// Add some interactive effects
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', function() {
        this.style.borderBottomColor = '#fff';
    });
    
    input.addEventListener('blur', function() {
        this.style.borderBottomColor = 'rgba(255, 255, 255, 0.5)';
    });
});'''
        
        # Write files
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')
        (project_path / 'style.css').write_text(css_content, encoding='utf-8')
        (project_path / 'script.js').write_text(js_content, encoding='utf-8')

    def create_dashboard(self, project_path: Path):
        """Create a dashboard template"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="dashboard">
        <nav class="sidebar">
            <h2>Admin Panel</h2>
            <ul>
                <li><a href="#" class="active">Dashboard</a></li>
                <li><a href="#">Users</a></li>
                <li><a href="#">Analytics</a></li>
                <li><a href="#">Settings</a></li>
            </ul>
        </nav>
        <main class="content">
            <header>
                <h1>Dashboard Overview</h1>
            </header>
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Users</h3>
                    <p>1,234</p>
                </div>
                <div class="stat-card">
                    <h3>Revenue</h3>
                    <p>₹45,678</p>
                </div>
                <div class="stat-card">
                    <h3>Orders</h3>
                    <p>567</p>
                </div>
            </div>
        </main>
    </div>
</body>
</html>'''
        
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: #f5f5f5;
}

.dashboard {
    display: flex;
    height: 100vh;
}

.sidebar {
    width: 250px;
    background: #2c3e50;
    color: white;
    padding: 20px;
}

.sidebar h2 {
    margin-bottom: 30px;
    text-align: center;
}

.sidebar ul {
    list-style: none;
}

.sidebar li {
    margin: 10px 0;
}

.sidebar a {
    color: white;
    text-decoration: none;
    padding: 10px;
    display: block;
    border-radius: 5px;
    transition: 0.3s;
}

.sidebar a:hover,
.sidebar a.active {
    background: #3498db;
}

.content {
    flex: 1;
    padding: 20px;
}

header h1 {
    margin-bottom: 30px;
    color: #2c3e50;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-card h3 {
    color: #7f8c8d;
    margin-bottom: 10px;
}

.stat-card p {
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
}'''
        
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')
        (project_path / 'style.css').write_text(css_content, encoding='utf-8')

    def create_portfolio(self, project_path: Path):
        """Create a portfolio website"""
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Portfolio</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <nav>
            <h1>John Doe</h1>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#projects">Projects</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <h2>Full Stack Developer</h2>
            <p>Creating amazing digital experiences</p>
            <button>View My Work</button>
        </div>
    </section>
    
    <section id="about" class="about">
        <h2>About Me</h2>
        <p>I'm a passionate developer with expertise in modern web technologies.</p>
    </section>
    
    <section id="projects" class="projects">
        <h2>My Projects</h2>
        <div class="project-grid">
            <div class="project-card">
                <h3>Project 1</h3>
                <p>Web Application</p>
            </div>
            <div class="project-card">
                <h3>Project 2</h3>
                <p>Mobile App</p>
            </div>
        </div>
    </section>
</body>
</html>'''
        
        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
}

header {
    background: #333;
    color: white;
    padding: 1rem 0;
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

nav ul {
    display: flex;
    list-style: none;
}

nav ul li {
    margin-left: 20px;
}

nav a {
    color: white;
    text-decoration: none;
    transition: 0.3s;
}

nav a:hover {
    color: #007bff;
}

.hero {
    height: 100vh;
    background: linear-gradient(135deg, #007bff, #6610f2);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
}

.hero-content h2 {
    font-size: 3rem;
    margin-bottom: 20px;
}

.hero-content p {
    font-size: 1.2rem;
    margin-bottom: 30px;
}

.hero-content button {
    padding: 12px 30px;
    background: transparent;
    border: 2px solid white;
    color: white;
    border-radius: 25px;
    cursor: pointer;
    transition: 0.3s;
}

.hero-content button:hover {
    background: white;
    color: #007bff;
}

section {
    padding: 80px 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.projects {
    background: #f8f9fa;
}

.project-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin-top: 30px;
}

.project-card {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    text-align: center;
}'''
        
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')
        (project_path / 'style.css').write_text(css_content, encoding='utf-8')

    def create_basic_website(self, project_path: Path, project_type: str):
        """Create a basic website template"""
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_type.title()}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f4f4f4;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{project_type.title()}</h1>
        <p>This is your {project_type} website. Start customizing it!</p>
    </div>
</body>
</html>'''
        
        (project_path / 'index.html').write_text(html_content, encoding='utf-8')

    def access_chatgpt(self, search_query: str = None):
        """Access ChatGPT and optionally search"""
        self.speak("ChatGPT open kar raha hun...")
        
        if search_query:
            # Create a more specific search URL for ChatGPT
            encoded_query = search_query.replace(' ', '%20')
            url = f"https://chat.openai.com/"
            webbrowser.open(url)
            
            # Wait a bit for page to load, then try to paste query
            time.sleep(5)
            try:
                # This will attempt to paste the query (requires user to click in text area)
                pyautogui.typewrite(search_query)
                self.speak(f"ChatGPT mein '{search_query}' type kar diya. Enter press kariye send karne ke liye.")
            except:
                self.speak(f"ChatGPT open ho gaya. Manually '{search_query}' search kariye.")
        else:
            webbrowser.open("https://chat.openai.com/")
            self.speak("ChatGPT open ho gaya! Kya search karna chahte hain?")
            search_input = self.get_user_input("🔍 Search query: ")
            if search_input:
                self.access_chatgpt(search_input)

    def read_screen(self, translate_to: str = None):
        """Read current screen content using OCR"""
        self.speak("Screen capture kar raha hun...")
        
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            screenshot_path = Path.home() / "Desktop" / f"screen_capture_{int(time.time())}.png"
            screenshot.save(screenshot_path)
            
            self.speak("Screen text extract kar raha hun...")
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(screenshot)
            
            if extracted_text.strip():
                print("\n📖 SCREEN CONTENT:")
                print("=" * 50)
                print(extracted_text)
                print("=" * 50)
                
                # Save to memory
                screen_entry = {
                    'text': extracted_text,
                    'timestamp': datetime.now().isoformat(),
                    'screenshot_path': str(screenshot_path)
                }
                self.memory_data['screen_readings'].append(screen_entry)
                self.save_memory()
                
                if translate_to:
                    self.translate_text(extracted_text, translate_to)
                else:
                    self.speak("Screen content successfully extract kar liya. Console mein dekh sakte hain.")
                    
                    # Ask if user wants translation
                    self.speak("Translation chahiye? Kya language mein convert karna hai?")
                    translate_input = self.get_user_input("🌍 Translate to (language): ")
                    if translate_input:
                        self.translate_text(extracted_text, translate_input)
            else:
                self.speak("Screen mein koi readable text nahi mila.")
                
        except Exception as e:
            self.speak(f"Screen reading error: {str(e)}")
            print("Note: OCR ke liye tesseract install karna padega: sudo apt install tesseract-ocr")

    def translate_text(self, text: str, target_language: str):
        """Translate text using AI"""
        self.speak(f"Text ko {target_language} mein translate kar raha hun...")
        
        try:
            system_content = f"""You are a professional translator. Translate the given text to {target_language}. 
            Provide accurate and natural translation. If the target language is not clear, try to understand from context.
            Common languages: Hindi, English, Spanish, French, German, Chinese, Japanese, etc."""
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Translate this text to {target_language}:\n\n{text}"}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=1000,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            print(f"\n🌍 TRANSLATION TO {target_language.upper()}:")
            print("=" * 50)
            print(translated_text)
            print("=" * 50)
            
            # Save translation
            translation_entry = {
                'original_text': text[:200] + "..." if len(text) > 200 else text,
                'translated_text': translated_text,
                'target_language': target_language,
                'timestamp': datetime.now().isoformat()
            }
            self.memory_data['translations'].append(translation_entry)
            self.memory_data['session_stats']['translations'] += 1
            self.save_memory()
            
            self.speak(f"Translation complete! {target_language} mein convert kar diya.")
            
        except Exception as e:
            self.speak(f"Translation error: {str(e)}")

    def generate_custom_code(self, description: str):
        """Generate custom code based on description"""
        self.speak("Custom code generate kar raha hun...")
        
        try:
            system_content = """You are an expert programmer. Generate clean, well-commented code based on user requirements.
            Provide complete, working code with proper structure. Include HTML, CSS, and JavaScript if it's a web project.
            Make the code production-ready and follow best practices."""
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Generate code for: {description}"}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=2000,
                temperature=0.3
            )
            
            generated_code = response.choices[0].message.content.strip()
            
            # Create file with generated code
            code_filename = f"generated_code_{int(time.time())}.txt"
            code_path = Path.home() / "Desktop" / code_filename
            
            with open(code_path, 'w', encoding='utf-8') as f:
                f.write(f"// Generated Code for: {description}\n")
                f.write(f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(generated_code)
            
            print(f"\n💻 GENERATED CODE:")
            print("=" * 50)
            print(generated_code[:500] + "..." if len(generated_code) > 500 else generated_code)
            print("=" * 50)
            
            # Save to memory
            code_entry = {
                'description': description,
                'code_preview': generated_code[:200] + "..." if len(generated_code) > 200 else generated_code,
                'file_path': str(code_path),
                'timestamp': datetime.now().isoformat()
            }
            self.memory_data['generated_code'].append(code_entry)
            self.save_memory()
            
            self.speak(f"Code successfully generate kar diya! Desktop pe {code_filename} file mein save hai.")
            
        except Exception as e:
            self.speak(f"Code generation error: {str(e)}")

    def analyze_command_intent(self, command: str) -> Dict[str, Any]:
        """Analyze command for coding-related intents"""
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
        
        # Check for VS Code commands
        if any(pattern in command for pattern in self.coding_patterns['open_vscode']):
            analysis['intent'] = 'open_vscode'
            analysis['confidence'] += 0.5
            
            # Check for project type
            for project_type, patterns in self.web_project_types.items():
                if any(pattern in command for pattern in patterns):
                    analysis['parameters'] = [project_type]
                    analysis['confidence'] += 0.4
                    break
        
        # Check for code generation
        elif any(pattern in command for pattern in self.coding_patterns['generate_code']):
            analysis['intent'] = 'generate_code'
            analysis['confidence'] += 0.5
            
            # Extract what to generate
            code_patterns = [
                r'banao\s+(.+)',
                r'create\s+(.+)',
                r'generate\s+(.+)',
                r'code\s+(.+)',
                r'website\s+(.+)',
                r'program\s+(.+)'
            ]
            
            for pattern in code_patterns:
                match = re.search(pattern, command)
                if match:
                    description = match.group(1).strip()
                    analysis['parameters'] = [description]
                    analysis['confidence'] += 0.3
                    break
        
        # Check for ChatGPT access
        elif any(pattern in command for pattern in self.coding_patterns['chatgpt_access']):
            analysis['intent'] = 'chatgpt_access'
            analysis['confidence'] += 0.5
            
            # Extract search query
            search_patterns = [
                r'(?:mein|me)\s+(.+)\s+search',
                r'search\s+(.+)',
                r'find\s+(.+)',
                r'ask\s+(.+)'
            ]
            
            for pattern in search_patterns:
                match = re.search(pattern, command)
                if match:
                    query = match.group(1).strip()
                    analysis['parameters'] = [query]
                    analysis['confidence'] += 0.3
                    break
        
        # Check for screen reading
        elif any(pattern in command for pattern in self.coding_patterns['screen_read']):
            analysis['intent'] = 'screen_read'
            analysis['confidence'] += 0.5
            
            # Check for translation request
            if any(word in command for word in ['translate', 'anuwad', 'convert']):
                translate_patterns = [
                    r'(?:translate|anuwad|convert)\s+(?:to|mein)\s+(\w+)',
                    r'(\w+)\s+(?:mein|me)\s+(?:translate|convert)',
                ]
                
                for pattern in translate_patterns:
                    match = re.search(pattern, command)
                    if match:
                        language = match.group(1).strip()
                        analysis['parameters'] = [language]
                        analysis['confidence'] += 0.3
                        break
        
        # Check for direct translation
        elif any(pattern in command for pattern in self.coding_patterns['translate']):
            analysis['intent'] = 'translate'
            analysis['confidence'] += 0.4
            analysis['needs_clarification'] = True
            analysis['clarification_type'] = 'translation_text'
        
        # Set confidence based on overall analysis
        if analysis['confidence'] < 0.5 and not analysis['needs_clarification']:
            analysis['needs_clarification'] = True
            if not analysis['clarification_type']:
                analysis['clarification_type'] = 'general_intent'
        
        return analysis

    def ask_clarification(self, analysis: Dict[str, Any], original_command: str) -> Dict[str, Any]:
        """Ask for clarification when needed"""
        clarification_type = analysis['clarification_type']
        
        if clarification_type == 'translation_text':
            self.speak("Kya text translate karna hai? Aur kya language mein?")
            text_input = self.get_user_input("📝 Text to translate: ")
            language_input = self.get_user_input("🌍 Target language: ")
            
            if text_input and language_input:
                analysis['parameters'] = [text_input, language_input]
                analysis['needs_clarification'] = False
                analysis['confidence'] = 0.9
        
        elif clarification_type == 'general_intent':
            ai_response = self.get_smart_clarification(original_command)
            self.speak(ai_response)
            
            clarification_input = self.get_user_input("🤔 Clarification: ")
            combined_command = f"{original_command} {clarification_input}"
            analysis = self.analyze_command_intent(combined_command)
        
        return analysis

    def get_smart_clarification(self, command: str) -> str:
        """Use AI to ask smart clarification questions"""
        try:
            system_content = """You are RJ, a coding assistant. User gave a command but it's not clear. 
            Ask a specific clarifying question in Hinglish to understand what they want.
            Focus on coding, web development, or tech-related clarifications."""
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Coding command unclear: '{command}'. What specific question should I ask?"}
            ]
            
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "Aap kya coding karna chahte hain? Detail mein batayiye."

    def execute_command(self, analysis: Dict[str, Any], original_command: str):
        """Execute the analyzed coding command"""
        intent = analysis['intent']
        parameters = analysis['parameters']
        
        self.memory_data['session_stats']['total_commands'] += 1
        
        try:
            if intent == 'open_vscode':
                project_type = parameters[0] if parameters else None
                self.open_vscode_with_project(project_type)
            
            elif intent == 'generate_code':
                description = parameters[0] if parameters else "basic website"
                self.generate_custom_code(description)
            
            elif intent == 'chatgpt_access':
                search_query = parameters[0] if parameters else None
                self.access_chatgpt(search_query)
            
            elif intent == 'screen_read':
                translate_to = parameters[0] if parameters else None
                self.read_screen(translate_to)
            
            elif intent == 'translate':
                if len(parameters) >= 2:
                    text, language = parameters[0], parameters[1]
                    self.translate_text(text, language)
                else:
                    self.speak("Translation ke liye text aur language dono chahiye.")
            
            else:
                # Use AI for general queries
                self.handle_ai_query(original_command)
                
        except Exception as e:
            self.speak(f"Error: {str(e)}")
            print(f"❌ Error executing command: {e}")

    def handle_ai_query(self, query: str):
        """Handle general AI queries with coding focus"""
        try:
            system_content = """You are RJ, an advanced coding assistant that speaks perfect Hinglish.
            You specialize in web development, programming, and technical guidance.
            Answer user queries helpfully with coding focus when relevant."""
            
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
            self.speak(ai_response)
            
        except Exception as e:
            self.speak("AI service mein problem hai. Sorry!")

    def process_command(self, command: str):
        """Main method to process coding commands"""
        if not command or command.lower() in ['exit', 'quit', 'bye']:
            self.speak("Alvida! Advanced Coding RJ band ho raha hai.")
            self.running = False
            return
        
        print("🤔 Analyzing coding command...")
        
        # Analyze command intent
        analysis = self.analyze_command_intent(command)
        print(f"📊 Intent: {analysis['intent']}, Confidence: {analysis['confidence']:.1f}")
        
        # Ask for clarification if needed
        if analysis['needs_clarification']:
            print("❓ Need clarification...")
            analysis = self.ask_clarification(analysis, command)
        
        # Execute command
        if not analysis['needs_clarification']:
            print("✅ Executing coding command...")
            self.execute_command(analysis, command)
        else:
            self.speak("Command samajh nahi aaya. Kya coding karna chahte hain?")

    def run(self):
        """Main run loop for coding assistant"""
        self.speak("Advanced Coding RJ ready hai! VS Code, code generation, ChatGPT, screen reading - sab kuch available hai!")
        
        while self.running:
            try:
                user_command = self.get_user_input()
                
                if user_command:
                    print(f"\n📝 Processing: '{user_command}'")
                    self.process_command(user_command)
                    print("\n" + "="*60 + "\n")
                
            except KeyboardInterrupt:
                self.speak("Alvida! Advanced Coding RJ band ho raha hai.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                self.speak("Kuch error aaya hai. Phir try kariye.")

def main():
    """Main function"""
    try:
        print("🚀 Starting Advanced Coding RJ...")
        rj = AdvancedCodingRJ()
        rj.run()
    except Exception as e:
        print(f"❌ Failed to start Advanced Coding RJ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()