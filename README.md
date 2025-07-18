# RJ Assistant - Personal AI Voice Assistant

🎙️ **RJ** is your personal AI assistant that speaks Hindi and English (Hinglish) and can control your laptop with voice commands.

## ✨ Features

### 🗣️ **Voice Recognition**
- Hindi and English voice commands
- Natural Hinglish conversation
- Smart wake word detection ("RJ")

### 🖥️ **System Control**
- Shutdown, restart, sleep, lock computer
- Volume control (up, down, mute)
- Application launching and closing

### 📁 **File Management**
- Create, rename, delete files
- Open files and folders
- File operations with voice commands

### 🌐 **Web Integration**
- Google search with voice
- YouTube search and navigation
- Website opening
- **Wikipedia integration** for instant information

### 📝 **Text Operations**
- Built-in text editor
- Voice note taking
- File reading and editing

### 🤖 **AI Powered**
- DeepSeek AI integration
- Contextual conversations
- Smart question answering

## 🚀 Quick Setup

### 1. Clone and Setup
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (installs all dependencies)
./setup.sh
```

### 2. Configure API Key
Your DeepSeek API key is already configured in `.env` file.

### 3. Start RJ Assistant
```bash
python3 rj_assistant.py
```

## 🎤 Voice Commands

### System Control
- **"RJ shutdown"** / **"RJ computer band kar"** - Shutdown system
- **"RJ restart"** / **"RJ dubara start kar"** - Restart system
- **"RJ volume badhao"** - Increase volume
- **"RJ volume kam kar"** - Decrease volume
- **"RJ mute kar"** - Toggle mute

### Applications
- **"RJ calculator kholo"** - Open calculator
- **"RJ text editor kholo"** - Open text editor
- **"RJ browser kholo"** - Open web browser
- **"RJ terminal kholo"** - Open terminal

### Information & Search
- **"RJ Wikipedia Mahatma Gandhi"** - Search Wikipedia
- **"RJ kya hai artificial intelligence"** - Ask questions
- **"RJ batao India ke bare mein"** - Get information
- **"RJ Google par search kar Python programming"** - Google search

### Web Browsing
- **"RJ YouTube kholo"** - Open YouTube
- **"RJ search for machine learning"** - Google search
- **"RJ website kholo github.com"** - Open websites

### File Operations
- **"RJ note likh important meeting tomorrow"** - Take voice notes
- **"RJ create file report.txt"** - Create files
- **"RJ rename file old.txt to new.txt"** - Rename files

## 📁 Project Structure

```
├── rj_assistant.py          # Main RJ Assistant (Hindi-English)
├── jarvis.py               # Basic JARVIS assistant
├── enhanced_jarvis.py      # Enhanced JARVIS with advanced features
├── text_editor.py          # Built-in text editor
├── requirements.txt        # Python dependencies
├── .env                   # API configuration
├── setup.sh              # Setup script
└── README.md             # This file
```

## 🔧 Technical Details

### Dependencies
- **Speech Recognition**: Google Speech Recognition
- **Text-to-Speech**: pyttsx3 with voice customization
- **AI Integration**: DeepSeek API via OpenAI client
- **Wikipedia**: Wikipedia Python library
- **System Control**: subprocess, psutil

### Voice Models
RJ Assistant automatically selects the best available voice on your system:
- Prioritizes female voices for better user experience
- Falls back to voice index [2] as requested
- Supports both Hindi and English pronunciation

### Language Support
- **Speech Recognition**: Hindi (hi-IN) and English (en-US)
- **Wikipedia**: Hindi and English content
- **AI Responses**: Natural Hinglish conversation

## 🛠️ Troubleshooting

### Audio Issues
```bash
# Install additional audio packages
sudo apt-get install pulseaudio alsa-utils

# Test microphone
arecord -l
```

### Permission Issues
```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Restart audio service
sudo systemctl restart pulseaudio
```

### Voice Recognition Problems
- Ensure microphone is working
- Speak clearly and close to microphone
- Check internet connection for Google Speech Recognition

## 🎯 Usage Examples

### Basic Commands
```
"RJ volume badhao"           → Increases volume
"RJ calculator kholo"        → Opens calculator
"RJ computer lock kar"       → Locks screen
```

### Information Queries
```
"RJ batao Taj Mahal ke bare mein"     → Wikipedia about Taj Mahal
"RJ kya hai machine learning"         → Explains ML
"RJ kaun hai Narendra Modi"          → Information about person
```

### Advanced Features
```
"RJ note likh meeting at 3 PM"       → Saves voice note
"RJ Google par search kar best restaurants" → Google search
"RJ YouTube par Bollywood songs"     → YouTube search
```

## 🔒 Security Features

- Safe system commands with confirmation
- File operation confirmations
- API key security with environment variables
- Error handling and recovery

## 🤝 Contributing

Feel free to enhance RJ Assistant:
1. Add new voice commands
2. Improve speech recognition
3. Add new features
4. Optimize performance

## 📄 License

This project is for personal use. DeepSeek API usage subject to their terms.

---

**Made with ❤️ for voice-controlled computing**

🎙️ **"RJ ready hai! Boliye kya kaam hai?"**