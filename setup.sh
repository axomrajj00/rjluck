#!/bin/bash

echo "🚀 RJ Assistant Setup Script"
echo "============================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install system dependencies for audio
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio espeak espeak-data libespeak1 libespeak-dev festival festvox-kallpc16k

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Make scripts executable
chmod +x rj_assistant.py
chmod +x jarvis.py
chmod +x enhanced_jarvis.py

echo "✅ Setup complete!"
echo ""
echo "🎙️ Available assistants:"
echo "1. RJ Assistant (Hindi-English): python3 rj_assistant.py"
echo "2. Basic JARVIS: python3 jarvis.py"
echo "3. Enhanced JARVIS: python3 enhanced_jarvis.py"
echo ""
echo "📋 Features:"
echo "• Voice commands in Hindi and English"
echo "• System control (shutdown, restart, volume)"
echo "• Application launching"
echo "• File operations"
echo "• Wikipedia search"
echo "• Text editor"
echo "• Web browsing"
echo "• AI-powered conversations"
echo ""
echo "🎤 Usage:"
echo "Say 'RJ' followed by your command"
echo "Examples:"
echo "• 'RJ Wikipedia search Mahatma Gandhi'"
echo "• 'RJ calculator kholo'"
echo "• 'RJ volume badhao'"
echo "• 'RJ kya hai artificial intelligence'"
echo ""
echo "🏃 To start RJ Assistant:"
echo "python3 rj_assistant.py"